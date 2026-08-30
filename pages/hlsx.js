/******************************************************************************/
//HlsPlayer with Subtitles v0.0.2 (hls.js v1.7.1)
//Original version (c) 2022 Benjamin Zachey
//related API: https://github.com/video-dev/hls.js
//
//KP-MSX patch: the track indicators in the top-right corner show the full
//track name from the HLS manifest (e.g. "01. Двухголосый. Twister (RUS)")
//instead of an uppercased 8-character prefix; quality choice is keyed by
//rendition height; playback position is reported to /msx/progress every
//10 s while it changes. All patches are marked.
/******************************************************************************/
function HlsPlayer() {
    var infoData = null;
    var hls = null;
    var player = null;
    var ready = false;
    var ended = false;

    //--------------------------------------------------------------------------
    //Progress reporting (KP-MSX patch)
    //--------------------------------------------------------------------------
    var PROGRESS_INTERVAL_MS = 10000;
    var progressTimer = null;
    var progressData = null;
    var lastSentPosition = -1;

    var readProgressParams = function() {
        var content_id = TVXServices.urlParams.get("content_id");
        if (!TVXTools.isFullStr(content_id)) {
            return null;
        }
        return {
            client_id: TVXServices.urlParams.get("client_id"),
            content_id: content_id,
            season: TVXServices.urlParams.get("season"),
            episode: TVXServices.urlParams.get("episode")
        };
    };

    var sendProgress = function(position) {
        if (progressData == null || !TVXTools.isFullStr(progressData.client_id)) {
            return;
        }
        position = Math.floor(position);
        if (position <= 0 || position === lastSentPosition) {
            return;
        }
        lastSentPosition = position;
        var parts = [];
        parts.push("id=" + encodeURIComponent(progressData.client_id));
        parts.push("content_id=" + encodeURIComponent(progressData.content_id));
        if (TVXTools.isFullStr(progressData.season)) {
            parts.push("season=" + encodeURIComponent(progressData.season));
        }
        if (TVXTools.isFullStr(progressData.episode)) {
            parts.push("episode=" + encodeURIComponent(progressData.episode));
        }
        parts.push("position=" + encodeURIComponent(position));

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/msx/progress?" + parts.join("&"), true);
        xhr.send();
    };

    var startProgressReporting = function() {
        if (progressTimer != null) {
            return;
        }
        progressData = readProgressParams();
        if (progressData == null) {
            return;
        }
        progressTimer = setInterval(function() {
            if (player != null && isFinite(player.duration)) {
                sendProgress(player.currentTime);
            }
        }, PROGRESS_INTERVAL_MS);
    };

    var stopProgressReporting = function() {
        if (progressTimer != null) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    };

    //--------------------------------------------------------------------------
    //Audio & Subtitle Tracks
    //Merged from HTML5X
    //--------------------------------------------------------------------------
    var PROPERTY_PREFIX = "hlsjs:";
    var SUBTITLES_KIND = "SUBTITLES";
    var CAPTIONS_KIND = "CLOSED-CAPTIONS";
    var PROXY_URL = TVXTools.getHostUrl("services/proxy.php?url={URL}");
    var useProxy = false;
    var showRelatedContent = false;
    var hasRelatedContent = false;
    var defaultAudioTrackName = null;
    var defaultSubtitleTrackIndex = -1;
    var audioTrackIndicator = null;
    var subtitleTrackIndicator = null;
    var defaultExtensionLabel = null;
    var setupCrossOrigin = function(info) {
        if (player != null) {
            if (TVXPropertyTools.getBool(info, PROPERTY_PREFIX + "cors", true)) {
                player.crossOrigin = "anonymous";
            } else {
                useProxy = true;
            }
        }
    };
    var setupRelatedContent = function(info) {
        showRelatedContent = TVXPropertyTools.getBool(info, PROPERTY_PREFIX + "content", false);
        hasRelatedContent = info != null && info.index >= 0;
    };
    var setupDefaultExtensionLabel = function(info) {
        defaultExtensionLabel = TVXPropertyTools.getFullStr(info, "label:extension", null);
    };
    var hasAudioTracks = function() {
        return hls != null && hls.audioTrackController != null && hls.audioTrackController.audioTracks != null && hls.audioTrackController.audioTracks.length > 0;
    };
    var hasTextTracks = function() {
        return hls != null && hls.subtitleTrackController != null && hls.subtitleTrackController.subtitleTracks != null && hls.subtitleTrackController.subtitleTracks.length > 0;
    };
    var hasQualityLevels = function () {
        return hls != null && hls.capLevelController != null && hls.levels.length > 0;
    }
    var foreachAudioTrack = function(callback) {
        if (hasAudioTracks() && typeof callback == "function") {
            var tracks = hls.audioTrackController.audioTracks;
            var length = hls.audioTrackController.audioTracks.length;
            for (var i = 0; i < length; i++) {
                if (callback(i, tracks[i]) === true) {
                    break;
                }
            }
        }
    };
    var foreachSubtitleTrack = function(callback) {
        if (hasTextTracks() && typeof callback == "function") {
            var tracks = hls.subtitleTrackController.subtitleTracks;
            var length = hls.subtitleTrackController.subtitleTracks.length;
            for (var i = 0; i < length; i++) {
                var track = tracks[i];
                if (track.type === SUBTITLES_KIND || track.type === CAPTIONS_KIND) {
                    if (callback(i, track) === true) {
                        break;
                    }
                }
            }
        }
    };
    var foreachQualityLevel = function(callback) {
        if (hasQualityLevels() && typeof callback == "function") {
            var levels = hls.levels;
            var length = hls.levels.length;
            for (var i = 0; i < length; i++) {
                var level = levels[i];
                if (callback(i, level) === true) {
                    break;
                }
            }
        }
    };
    var isAudioTrackSelected = function(track) {
        return track != null && hls.audioTrackController.audioTrack === track.id;
    };
    var isSubtitleTrackSelected = function(track) {
        return track != null && hls.subtitleTrackController.subtitleTrack === track.id;
    };
    var isQualityLevelSelected = function(level) {
        return level != null && getStoredQualityLevel() == level.height.toString();
    };
    var createIndexTrack = function(index, track) {
        if (index >= 0 && track != null) {
            return {
                index: index,
                track: track
            };
        }
        return null;
    };
    var getAudioTrackLabel = function(indexTrack) {
        var index = indexTrack != null ? indexTrack.index : -1;
        var track = indexTrack != null ? indexTrack.track : null;
        if (index >= 0 && track != null) {
            return (TVXTools.isFullStr(track.name) ? track.name : "Audio Track " + (index + 1));
        }
        return hasAudioTracks() ? "None" : "Original";
    };
    var getSubtitleTrackLabel = function(indexTrack) {
        var index = indexTrack != null ? indexTrack.index : -1;
        var track = indexTrack != null ? indexTrack.track : null;
        if (index >= 0 && track != null) {
            return (TVXTools.isFullStr(track.name) ? track.name : "Subtitles " + (index + 1));
        }
        return "Off";
    };
    var getQualityLevelLabel = function(indexLevel) {
        var index = indexLevel != null ? indexLevel.index : -1;
        var track = indexLevel != null ? indexLevel.track : null;
        if (index >= 0 && track != null) {
            return indexLevel.track.width + "x" + indexLevel.track.height;
        }
        return "Auto";
    };
    var storeAudioTrack = function(track) {
        if (track != null && TVXTools.isFullStr(track.name)) {
            TVXServices.storage.set(PROPERTY_PREFIX + "audiotrack", track.name);
        } else {
            TVXServices.storage.remove(PROPERTY_PREFIX + "audiotrack");
        }
    };
    var getStoredAudioTrack = function() {
        return TVXServices.storage.get(PROPERTY_PREFIX + "audiotrack")
    }
    var storeSubtitleTrack = function(track) {
        if (track != null && TVXTools.isFullStr(track.name)) {
            TVXServices.storage.set(PROPERTY_PREFIX + "subtitle", track.name);
        } else {
            TVXServices.storage.remove(PROPERTY_PREFIX + "subtitle");
        }
    };
    var getStoredSubtitleTrack = function() {
        return TVXServices.storage.get(PROPERTY_PREFIX + "subtitle")
    }
    var storeQualityLevel = function(level) {
        if (level != null && level.height != null && TVXTools.isFullStr(level.height.toString())) {
            TVXServices.storage.set(PROPERTY_PREFIX + "qualityLevel", level.height);
        } else {
            TVXServices.storage.remove(PROPERTY_PREFIX + "qualityLevel");
        }
    };
    var getStoredQualityLevel = function() {
        return TVXServices.storage.get(PROPERTY_PREFIX + "qualityLevel")
    }
    var setupAudioTrackIndicator = function(track) {
        if (track != null && TVXTools.isFullStr(track.name)) {
            //KP-MSX patch: full manifest name, no uppercase/truncation
            audioTrackIndicator = "{ico:msx-white:audiotrack} " + track.name;
        } else {
            audioTrackIndicator = null;
        }
    };
    var setupSubtitleTrackIndicator = function(track) {
        if (track != null && TVXTools.isFullStr(track.name)) {
            //KP-MSX patch: full manifest name, no uppercase/truncation
            subtitleTrackIndicator = "{ico:msx-white:subtitles} " + track.name;
        } else {
            subtitleTrackIndicator = null;
        }
    };
    var setupExtensionLabel = function(label) {
        if (defaultExtensionLabel != null && label != null) {
            TVXVideoPlugin.setupExtensionLabel(label + " " + defaultExtensionLabel);
        } else if (label != null) {
            TVXVideoPlugin.setupExtensionLabel(label);
        } else {
            TVXVideoPlugin.setupExtensionLabel(defaultExtensionLabel);
        }
    };
    var applyIndicators = function() {
        if (audioTrackIndicator != null && subtitleTrackIndicator != null) {
            setupExtensionLabel(audioTrackIndicator + " " + subtitleTrackIndicator);
        } else if (audioTrackIndicator != null) {
            setupExtensionLabel(audioTrackIndicator);
        } else if (subtitleTrackIndicator != null) {
            setupExtensionLabel(subtitleTrackIndicator);
        } else {
            setupExtensionLabel(null);
        }
    };
    var selectAudioTrack = function(trackIndex, store, apply) {
        var selectedTrack = null;
        foreachAudioTrack(function(index, track) {
            if (index == trackIndex) {
                selectedTrack = track;

                var opts = {}
                if (track.name) opts['name'] = track.name;
                //TVXVideoPlugin.debug("Selecting audio track: " + JSON.stringify(opts));
                hls.setAudioOption(opts);
            }
        });
        setupAudioTrackIndicator(selectedTrack);
        if (store === true) {
            storeAudioTrack(selectedTrack);
        }
        if (apply === true) {
            applyIndicators();
        }
    };

    var selectSubtitleTrack = function(trackIndex, store, apply) {
        var selectedTrack = null;
        if (trackIndex === -1) {
            hls.subtitleTrackController.subtitleTrack = -1;
        } else {
            foreachSubtitleTrack(function(index, track) {
                if (index == trackIndex) {
                    selectedTrack = track;
                    
                    var opts = {}
                    if (track.name) opts['name'] = track.name;
                    //TVXVideoPlugin.debug("Selecting subtitles track: " + JSON.stringify(opts));
                    hls.setSubtitleOption(opts);

                    //hls.subtitleTrackController.subtitleTrack = index;
                }
            });
        }

        setupSubtitleTrackIndicator(selectedTrack);
        if (store === true) {
            storeSubtitleTrack(selectedTrack);
        }
        if (apply === true) {
            applyIndicators();
        }
    };
    var selectQualityLevel = function(trackIndex, store, apply) {
        var selectedLevel = null;
        if (trackIndex === -1) {
            hls.autoLevelCapping = 99;
            hls.currentLevel = hls.levels.length - 1
        } else {
            foreachQualityLevel(function(index, level) {
                if (index == trackIndex) {
                    //TVXVideoPlugin.debug("Selecting quality cap: " + JSON.stringify(level) + '/' + index);
                    selectedLevel = level;
                    hls.autoLevelCapping = index;
                    hls.currentLevel = index
                }
            });
        }
        if (store === true) {
            storeQualityLevel(selectedLevel);
        }
    };
    var getDefaultAudioTrackIndex = function() {
        var trackIndex = -1;
        var fallbackTrackIndex = -1;
        var storedTrackName = getStoredAudioTrack();
        foreachAudioTrack(function(index, track) {
            if (fallbackTrackIndex == -1) {
                //Fallback to first audio track
                fallbackTrackIndex = index;
            }
            if (storedTrackName === track.name) {
                trackIndex = index;
                return true;//break
            }
        });
        return trackIndex >= 0 ? trackIndex : fallbackTrackIndex;
    };
    var getDefaultSubtitleTrackIndex = function() {
        var trackIndex = -1;
        var fallbackTrackIndex = -1;
        var storedTrackName = getStoredSubtitleTrack();
        foreachSubtitleTrack(function(index, track) {
            if (storedTrackName === track.name) {
                trackIndex = index;
                return true;//break
            }
        });
        return trackIndex >= 0 ? trackIndex : fallbackTrackIndex;
    };
    var getDefaultQualityLevelIndex = function() {
        var levelIndex = -1;
        var fallbackLevelIndex = -1;
        var storedQualityLevel = getStoredQualityLevel();
        foreachQualityLevel(function(index, track) {
            if (fallbackLevelIndex == -1) {
                //Fallback to first quality level
                fallbackLevelIndex = index;
            }
            if (storedQualityLevel === track.height.toString()) {
                levelIndex = index;
                return true;//break
            }
        });
        return levelIndex >= 0 ? levelIndex : fallbackLevelIndex;
    };
    var getSelectedAudioIndexTrack = function() {
        var indexTrack = null;
        foreachAudioTrack(function(index, track) {
            if (isAudioTrackSelected(track)) {
                indexTrack = createIndexTrack(index, track);
                return true;//break
            }
        });
        return indexTrack;
    };
    var getSelectedSubtitleIndexTrack = function() {
        var indexTrack = null;
        foreachSubtitleTrack(function(index, track) {
            if (isSubtitleTrackSelected(track)) {
                indexTrack = createIndexTrack(index, track);
                return true;//break
            }
        });
        return indexTrack;
    };
    var getSelectedQualityIndexLevel = function() {
        var indexLevel = null;
        foreachQualityLevel(function(index, level) {
            if (isQualityLevelSelected(level)) {
                indexLevel = createIndexTrack(index, level);
                return true;//break
            }
        });
        return indexLevel;
    };
    var hasSelectedSubtitleTrack = function() {
        return getSelectedSubtitleIndexTrack() != null;
    };
    var setupAudioTracks = function(info) {
        defaultAudioTrackName = TVXPropertyTools.getFullStr(info, PROPERTY_PREFIX + "audiotrack", TVXServices.storage.get(PROPERTY_PREFIX + "audiotrack"));
        if (defaultAudioTrackName == "default") {
            defaultAudioTrackName = null;//Select first audio track
        }
    };
    var processSubtitleTrackCues = function(cues) {
        if (cues != null && cues.length > 0) {
            var length = cues.length;
            //Note: On some platforms (e.g. chrome browsers and android devices), this will have no effect
            for (var i = 0; i < length; i++) {
                var cue = cues[i];
                cue.snapToLines = true;//Use integer number of lines (default is true)
                cue.line = -3;//Move the cue up to get some space at the bottom (default is -1)
            }
        }
    };
    var applySubtitleTrackCues = function() {
        foreachSubtitleTrack(function(index, track) {
            track.oncuechange = function() {
                processSubtitleTrackCues(this.activeCues);
            };
        });
    };
    var secureSubtitleSource = function(src) {
        return TVXTools.isSecureContext() ? TVXTools.secureUrl(src) : src;
    };
    var createSubtitleSource = function(src) {
        return useProxy && TVXTools.isHttpUrl(src) ? TVXTools.strReplace(PROXY_URL, "{URL}", TVXTools.strToUrlStr(src)) : src;
    };
    var createSubtitleTrack = function(subtitle, src) {
        if (TVXTools.isFullStr(subtitle) && TVXTools.isFullStr(src)) {
            var separator = subtitle.indexOf(":");
            if (separator > 0) {
                return {
                    label: subtitle.substr(separator + 1),
                    language: subtitle.substr(0, separator),
                    src: secureSubtitleSource(createSubtitleSource(src))
                };
            }
        }
        return null;
    };
    var completeSubtitleTracks = function(completeState, tracks, callback) {
        if (completeState != null) {
            completeState.size--;
            if (completeState.size == 0 && typeof callback == "function") {
                callback(tracks);
            }
        }
    };
    var resolveSubtitleTrack = function(completeState, track, tracks, callback) {
        if (track != null && !TVXTools.isHttpUrl(track.src)) {
            TVXVideoPlugin.requestInteractionResponse(track.src, function(data) {
                if (TVXTools.isFullStr(data.error)) {
                    TVXVideoPlugin.error(data.error);
                } else if (data.response != null && TVXTools.isHttpUrl(data.response.url)) {
                    track.src = createSubtitleSource(data.response.url);
                } else {
                    TVXVideoPlugin.warn("Track URL is missing or invalid");
                }
                completeSubtitleTracks(completeState, tracks, callback);
            });
        } else {
            completeSubtitleTracks(completeState, tracks, callback);
        }
    };
    var createSubtitleTracks = function(info, callback) {
        var tracks = [];
        var prefix = PROPERTY_PREFIX + "subtitle:";
        var prefixLength = prefix.length;
        var order = TVXPropertyTools.getFullStr(info, prefix + "order", null);
        TVXPropertyTools.foreach(info, function(key, value) {
            if (TVXTools.isFullStr(key) && key.indexOf(prefix) == 0) {
                var track = createSubtitleTrack(key.substr(prefixLength), value);
                if (track != null) {
                    tracks.push(track);
                }
            }
        });
        if (tracks.length > 1 && order != null) {
            tracks.sort(function(track1, track2) {
                if (order == "label") {
                    return track1.name.localeCompare(track2.name);
                } else if (order == "language") {
                    return track1.lang.localeCompare(track2.lang);
                }
                return 0;
            });
        }
        if (tracks.length > 0) {
            var completeState = {
                size: tracks.length
            };
            for (var i = 0; i < tracks.length; i++) {
                resolveSubtitleTrack(completeState, tracks[i], tracks, callback);
            }
        } else if (typeof callback == "function") {
            callback(tracks);
        }
    };

    var setupVideoInfo = function(data, callback) {
        var info = data != null && data.video != null ? data.video.info : null;
        setupCrossOrigin(info);
        setupRelatedContent(info);
        setupDefaultExtensionLabel(info);
        setupAudioTracks(info);
        setupSubtitleTracks(info, callback);
    };
    //--------------------------------------------------------------------------

    //--------------------------------------------------------------------------
    //Player Options
    //Merged from HTML5X
    //--------------------------------------------------------------------------
    var currentOptionsFocus = null;
    var isFullscreenSupported = function() {
        if (infoData != null && TVXTools.isFullStr(infoData.platform)) {
            //Currently, the fullscreen mode only works properly on iOS/Mac devices
            return  infoData.platform.indexOf("ios") >= 0 ||
                    infoData.platform.indexOf("mac") >= 0;
        }
        return false;
    };
    var createTrackItem = function(type, index, label, selected) {
        return {
            focus: selected,
            label: label,
            extensionIcon: selected ? "check" : "blank",
            action: selected ? "back" : "player:commit:message:" + type + ":" + index
        };
    };
    var createAudioTracksPanel = function() {
        var items = [];
        if (hasAudioTracks()) {
            foreachAudioTrack(function(index, track) {
                items.push(createTrackItem("audiotrack", index, getAudioTrackLabel(createIndexTrack(index, track)), isAudioTrackSelected(track)));
            });
        } else {
            items.push(createTrackItem("audiotrack", -1, getAudioTrackLabel(null), true));
        }
        return {
            cache: false,
            reuse: false,
            headline: "Audio",
            template: {
                enumerate: false,
                type: "control",
                layout: "0,0,8,1"
            },
            items: items
        };
    };
    var createSubtitleTracksPanel = function() {
        var items = [createTrackItem("subtitle", -1, "Off", !hasSelectedSubtitleTrack())];
        foreachSubtitleTrack(function(index, track) {
            items.push(createTrackItem("subtitle", index, getSubtitleTrackLabel(createIndexTrack(index, track)), isSubtitleTrackSelected(track)));
        });
        return {
            cache: false,
            reuse: false,
            headline: "Subtitles",
            template: {
                enumerate: false,
                type: "control",
                layout: "0,0,8,1"
            },
            items: items
        };
    };
    var createQualityLevelPanel = function() {
        var items = [createTrackItem("quality", -1, getQualityLevelLabel(null), isQualityLevelSelected(null))];
        foreachQualityLevel(function(index, level) {
            items.push(createTrackItem("quality", index, getQualityLevelLabel(createIndexTrack(index, level)), isQualityLevelSelected(level)));
        });
        return {
            cache: false,
            reuse: false,
            headline: "Quality",
            template: {
                enumerate: false,
                type: "control",
                layout: "0,0,8,1"
            },
            items: items
        };
    };
    var createOptionsPanel = function() {
        var selectedAudioIndexTrack = getSelectedAudioIndexTrack();
        var selectedSubtitleIndexTrack = getSelectedSubtitleIndexTrack();
        var selectedQualityLevel = getSelectedQualityIndexLevel();
        var showFullscreen = isFullscreenSupported() && TVXVideoPlugin.isFullscreenEnabled(player);
        return {
            cache: false,
            reuse: false,
            headline: "Options",
            template: {
                enumerate: false,
                type: "control",
                layout: "0,0,8,1"
            },
            items: [{
                    focus: currentOptionsFocus == "audiotrack",
                    id: "audiotrack",
                    icon: "audiotrack",
                    label: "Audio",
                    extensionLabel: getAudioTrackLabel(selectedAudioIndexTrack),
                    action: "[player:commit:message:focus:audiotrack|panel:request:player:audiotrack]"
                }, {
                    focus: currentOptionsFocus == "subtitle",
                    id: "subtitle",
                    icon: "subtitles",
                    label: "Subtitles",
                    extensionLabel: getSubtitleTrackLabel(selectedSubtitleIndexTrack),
                    action: "[player:commit:message:focus:subtitle|panel:request:player:subtitle]"
                }, {
                    focus: currentOptionsFocus == "quality",
                    id: "quality",
                    icon: "high-quality",
                    label: "Quality",
                    extensionLabel: getQualityLevelLabel(selectedQualityLevel),
                    action: "[player:commit:message:focus:quality|panel:request:player:quality]"
                },
            //  {
            //        focus: currentOptionsFocus == "settings",
            //        id: "settings",
            //        icon: "settings",
            //        label: "Settings",
            //        action: "[player:commit:message:focus:settings|panel:request:player:settings]"
            //    }, 
                {
                    display: showFullscreen,
                    offset: "0,0.25,0,0",
                    focus: currentOptionsFocus == "fullscreen",
                    id: "fullscreen",
                    icon: "fullscreen",
                    label: "Fullscreen",
                    action: "[player:commit:message:focus:fullscreen|player:commit:message:fullscreen]"
                }, {
                    display: showRelatedContent,
                    offset: showFullscreen ? "0,0.5,0,0" : "0,0.25,0,0",
                    enable: hasRelatedContent,
                    focus: currentOptionsFocus == "content",
                    id: "content",
                    icon: "pageview",
                    label: "Related Content",
                    action: "[player:commit:message:focus:content|player:content]"
                }]
        };
    };

    var handleMessage = function(message) {
        if (TVXTools.isFullStr(message)) {
            if (message.indexOf("focus:") == 0) {
                currentOptionsFocus = message.substr(6);
            } else if (message.indexOf("audiotrack:") == 0) {
                TVXVideoPlugin.executeAction("cleanup");
                selectAudioTrack(TVXTools.strToNum(message.substr(11), -1), true, true);
            } else if (message.indexOf("subtitle:") == 0) {
                TVXVideoPlugin.executeAction("cleanup");
                selectSubtitleTrack(TVXTools.strToNum(message.substr(9), -1), true, true);
            } else if (message.indexOf("quality:") == 0) {
                TVXVideoPlugin.executeAction("cleanup");
                selectQualityLevel(TVXTools.strToNum(message.substr(8), -1), true, true);
            } else if (message == "fullscreen") {
                TVXVideoPlugin.executeAction("cleanup");
                TVXVideoPlugin.requestFullscreen(player);
            } else if (message.indexOf("settings:") == 0) {
                //TVXVideoPlugin.executeAction("cleanup");
                handleSettings(message)
            } else {
                TVXVideoPlugin.warn("Unknown plugin message: '" + message + "'");
            }
        }
    };
    var createResponseData = function(dataId) {
        if (TVXTools.isFullStr(dataId)) {
            if (dataId == "options") {
                return createOptionsPanel();
            } else if (dataId == "audiotrack") {
                return createAudioTracksPanel();
            } else if (dataId == "subtitle") {
                return createSubtitleTracksPanel();
            } else if (dataId == "quality") {
                return createQualityLevelPanel();
            }
        }
        return null;
    };
    //--------------------------------------------------------------------------

    //--------------------------------------------------------------------------
    //Event Callbacks
    //--------------------------------------------------------------------------

    var onWaiting = function() {
        TVXVideoPlugin.startLoading();
    };
    var onPlaying = function() {
        TVXVideoPlugin.stopLoading();
        TVXVideoPlugin.setState(TVXVideoState.PLAYING);
    };
    var onPaused = function() {
        TVXVideoPlugin.stopLoading();
        TVXVideoPlugin.setState(TVXVideoState.PAUSED);
    };
    var onContinue = function() {
        TVXVideoPlugin.stopLoading();
    };
    var onReady = function() {
        if (player != null && !ready) {
            ready = true;
            TVXVideoPlugin.debug("HLS video ready");
            // selectAudioTrack(getDefaultAudioTrackIndex(), false, false);
            selectSubtitleTrack(getDefaultSubtitleTrackIndex(), false, true);
            // selectQualityLevel(getDefaultQualityLevelIndex(), false, true);
            TVXVideoPlugin.applyVolume();
            TVXVideoPlugin.stopLoading();
            TVXVideoPlugin.startPlayback(true);//Accelerated start
        }
    };
    var onManifestLoaded = function(event, data) {
        selectAudioTrack(getDefaultAudioTrackIndex(), false, false);
        //selectSubtitleTrack(getDefaultSubtitleTrackIndex(), false, true);
        selectQualityLevel(getDefaultQualityLevelIndex(), false, true);
    };
    var onBufferAppended = function(event, data) {
        if (data.type === 'video' && player.buffered.length > 0) {
			const start = player.buffered.start(0);
			if (start > 0.5 && player.currentTime < start) {
			  player.currentTime = start;
			  player.play();
			}
		}
    };
    var getErrorText = function(code) {
        if (code == 1) {
            //The fetching of the associated resource was aborted by the user's request.
            return "Playback Aborted";
        } else if (code == 2) {
            //Some kind of network error occurred which prevented the media from being successfully fetched, despite having previously been available.
            return "Network Error";
        } else if (code == 3) {
            //Despite having previously been determined to be usable, an error occurred while trying to decode the media resource, resulting in an error.
            return "Media Decode Error";
        } else if (code == 4) {
            //The associated resource or media provider object (such as a MediaStream) has been found to be unsuitable.
            return "Source Not Supported";
        }
        return "Unknown Error";
    };
    var getErrorMessage = function(code, message) {
        var msg = code + ": " + getErrorText(code);
        if (TVXTools.isFullStr(message)) {
            msg += ": " + message;
        }
        return msg;
    };
    var onError = function() {
        if (player != null && player.error != null) {
            TVXVideoPlugin.error("HLS video error: " + getErrorMessage(player.error.code, player.error.message));
            TVXVideoPlugin.stopLoading();
        }
    };
    var onEnded = function() {
        if (!ended) {
            ended = true;
            TVXVideoPlugin.debug("HLS video ended");
            sendProgress(player != null ? player.currentTime : 0);
            stopProgressReporting();
            TVXVideoPlugin.stopPlayback();
        }
    };
    var handleErrors = function() {
        if (hls != null) {
            hls.on(Hls.Events.ERROR, function(event, data) {
                if (hls != null && data.fatal) {
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            TVXVideoPlugin.error("HLS error: Fatal network error encountered, try to recover");
                            hls.startLoad();
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            TVXVideoPlugin.error("HLS error: Fatal media error encountered, try to recover");
                            hls.recoverMediaError();
                            break;
                        default:
                            TVXVideoPlugin.error("HLS error: Fatal error encountered, destroy instance");
                            hls.destroy();
                            hls = null;
                            break;
                    }
                }
            });
        }
    };

    this.init = function() {
        player = document.getElementById("player");
        player.addEventListener("canplay", onReady);
        player.addEventListener("error", onError);
        player.addEventListener("ended", onEnded);
        player.addEventListener("waiting", onWaiting);
        player.addEventListener("play", onContinue);
        player.addEventListener("playing", onPlaying);
        player.addEventListener("pause", onPaused);
        player.addEventListener("seeked", onContinue);
        player.addEventListener("abort", onContinue);
    };
    this.ready = function() {
        if (player != null) {
            TVXVideoPlugin.debug("Video plugin ready");
            var url = TVXServices.urlParams.get("url");
            if (TVXTools.isFullStr(url)) {
                TVXVideoPlugin.startLoading();

                if (Hls.isSupported()) {
                    hls = new Hls({
                      renderTextTracksNatively: true,
                    });

                    hls.loadSource(url);
                    hls.attachMedia(player);
                    hls.on(Hls.Events.MANIFEST_LOADED, onManifestLoaded);
					hls.on(Hls.Events.BUFFER_APPENDED, onBufferAppended);
                    handleErrors();
                } else {
                    player.src = url;
                    player.load();
                }
                startProgressReporting();
            } else {
                TVXVideoPlugin.warn("HLS URL is missing or empty");
            }
        } else {
            TVXVideoPlugin.error("HLS player is not initialized");
        }
    };
    this.dispose = function() {
        if (player != null) {
            player.removeEventListener("canplay", onReady);
            player.removeEventListener("error", onError);
            player.removeEventListener("ended", onEnded);
            player.removeEventListener("waiting", onWaiting);
            player.removeEventListener("play", onContinue);
            player.removeEventListener("playing", onPlaying);
            player.removeEventListener("pause", onPaused);
            player.removeEventListener("seeked", onContinue);
            player.removeEventListener("abort", onContinue);
            player = null;
        }
        if (hls != null) {
            hls.destroy();
            hls = null;
        }
        stopProgressReporting();
    };
    this.play = function() {
        if (player != null) {
            player.play();
        }
    };
    this.pause = function() {
        if (player != null) {
            player.pause();
        }
    };
    this.stop = function() {
        if (player != null) {
            //Note: Html5 player does not support stop -> use pause
            player.pause();
        }
    };
    this.getDuration = function() {
        if (player != null) {
            return player.duration;
        }
        return 0;
    };
    this.getPosition = function() {
        if (player != null) {
            return player.currentTime;
        }
        return 0;
    };
    this.setPosition = function(position) {
        if (player != null) {
            player.currentTime = position;
        }
    };
    this.setVolume = function(volume) {
        if (player != null) {
            player.volume = volume / 100;
        }
    };
    this.getVolume = function() {
        if (player != null) {
            return player.volume * 100;
        }
        return 100;
    };
    this.setMuted = function(muted) {
        if (player != null) {
            player.muted = muted;
        }
    };
    this.isMuted = function() {
        if (player != null) {
            return player.muted;
        }
        return false;
    };
    this.getSpeed = function() {
        if (player != null) {
            return player.playbackRate;
        }
        return 1;
    };
    this.setSpeed = function(speed) {
        if (player != null) {
            player.playbackRate = speed;
        }
    };
    this.getUpdateData = function() {
        return {
            position: this.getPosition(),
            duration: this.getDuration(),
            speed: this.getSpeed()
        };
    };

    this.handleData = function(data) {
        handleMessage(data.message);
    };
    this.handleRequest = function(dataId, data, callback) {
        callback(createResponseData(dataId));
    };
}
/******************************************************************************/

/******************************************************************************/
//Setup
/******************************************************************************/
TVXPluginTools.onReady(function() {
    TVXVideoPlugin.setupPlayer(new HlsPlayer());
    TVXVideoPlugin.init();
});
/******************************************************************************/