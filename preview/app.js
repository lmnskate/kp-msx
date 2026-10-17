'use strict';

/* ==========================================================================
   KP-MSX · KinoPub TV — прототип дизайна.
   Все данные вымышленные, бэкенда нет. Управление: стрелки / Enter / Backspace.
   ========================================================================== */

/* ------------------------------ Данные ---------------------------------- */

const TITLES = [
  {
    id: 'frontier', name: 'Последний рубеж', type: 'movie', year: 2025,
    genres: ['фантастика', 'триллер'], kp: 8.1, imdb: 7.9, dur: '2 ч 18 мин', mins: 138, q4k: true,
    grad: ['#173a6b', '#0e8a8a'],
    desc: 'Экипаж дальней разведки ловит с необитаемой планеты сигнал, которого не должно существовать. Капитан Волков решает высадиться — и с этого момента обратного пути у экспедиции уже нет.',
    cast: ['Артём Волков', 'Мария Соколова', 'Игорь Грант', 'Полина Рейн', 'Олег Дорн'],
    progress: { pos: 0.42 },
  },
  {
    id: 'harbor', name: 'Тихая гавань', type: 'serial', year: 2024,
    genres: ['драма', 'детектив'], kp: 7.8, imdb: 8.0, dur: '2 сезона', q4k: false,
    grad: ['#3a1c54', '#8a2b5e'],
    desc: 'В маленьком приморском городке пропадает рыбак. Следователь из столицы постепенно понимает: у каждого жителя гавани есть что скрывать, а тишина здесь — лишь видимость.',
    cast: ['Елена Морозова', 'Дмитрий Кранц', 'Вера Ладо', 'Семён Уткин'],
    progress: { pos: 0.3, s: 1, e: 2 },
    seasons: [
      { name: 'Сезон 1', episodes: [
        { n: 1, name: 'Прилив', dur: '49 мин', watched: true },
        { n: 2, name: 'Отлив', dur: '47 мин', watched: true },
        { n: 3, name: 'Туман', dur: '51 мин', watched: true },
        { n: 4, name: 'Маяк', dur: '48 мин', watched: true },
        { n: 5, name: 'Тишина', dur: '50 мин', watched: true },
        { n: 6, name: 'Шторм', dur: '52 мин', watched: true },
        { n: 7, name: 'Дно', dur: '49 мин', watched: true },
        { n: 8, name: 'Берег', dur: '54 мин', watched: true },
      ]},
      { name: 'Сезон 2', episodes: [
        { n: 1, name: 'Возвращение', dur: '50 мин', watched: true },
        { n: 2, name: 'Находка', dur: '48 мин', watched: true },
        { n: 3, name: 'Свидетель', dur: '49 мин', watched: true },
        { n: 4, name: 'Ложный след', dur: '47 мин', watched: false },
        { n: 5, name: 'Признание', dur: '51 мин', watched: false },
        { n: 6, name: 'Развязка', dur: '55 мин', watched: false },
      ]},
    ],
  },
  {
    id: 'northwind', name: 'Северный ветер', type: 'movie', year: 2025,
    genres: ['приключения', 'драма'], kp: 7.4, imdb: 7.1, dur: '1 ч 56 мин', mins: 116, q4k: true,
    grad: ['#0f4c5c', '#5f6caf'],
    desc: 'Полярный пилот соглашается на последний рейс к заброшенной станции, чтобы вывезти оттуда человека, которого все считали погибшим десять лет назад.',
    cast: ['Никита Орлов', 'Алина Звягина', 'Пётр Санин'],
  },
  {
    id: 'wires', name: 'Город на проводах', type: 'serial', year: 2025,
    genres: ['киберпанк', 'триллер'], kp: 8.4, imdb: 8.2, dur: '1 сезон', q4k: true,
    grad: ['#1a1a40', '#e94560'],
    desc: 'Мегаполис, где память можно арендовать по подписке. Хакерша по прозвищу Спица находит в чужих воспоминаниях заказ на саму себя.',
    cast: ['Кира Монро', 'Тимур Аделей', 'Жанна Фрост'],
    progress: { pos: 0.6, s: 0, e: 0 },
  },
  {
    id: 'ashes', name: 'Пепел и звёзды', type: 'movie', year: 2024,
    genres: ['драма', 'история'], kp: 7.9, imdb: 7.6, dur: '2 ч 04 мин', mins: 124, q4k: false,
    grad: ['#532407', '#c96f2e'],
    desc: 'После пожара, уничтожившего провинциальный театр, его труппа решает поставить последний спектакль прямо среди руин.',
    cast: ['Людмила Гарина', 'Степан Вейс', 'Антон Рудаков'],
    progress: { pos: 0.68 },
  },
  {
    id: 'curator', name: 'Куратор', type: 'serial', year: 2023,
    genres: ['триллер', 'криминал'], kp: 8.0, imdb: 7.8, dur: '1 сезон', q4k: false,
    grad: ['#101820', '#4e6e58'],
    desc: 'Хранитель запасников музея случайно узнаёт, что похищенные картины находит не полиция, а анонимный «куратор» — и решает выйти на него сам.',
    cast: ['Григорий Миллер', 'Ольга Тур', 'Руслан Кейт'],
    progress: { pos: 0.55, s: 0, e: 4 },
  },
  {
    id: 'lake', name: 'Мёртвое озеро', type: 'movie', year: 2025,
    genres: ['хоррор', 'мистика'], kp: 6.3, imdb: 5.9, dur: '1 ч 38 мин', mins: 98, q4k: false,
    grad: ['#0b0c10', '#5c2018'],
    desc: 'Компания блогеров приезжает снимать репортаж о затопленной деревне и обнаруживает, что колокол под водой звонит до сих пор.',
    cast: ['Вика Ренц', 'Марк Гладков', 'Соня Берг'],
  },
  {
    id: 'nighttrain', name: 'Ночной рейс', type: 'movie', year: 2025,
    genres: ['боевик', 'триллер'], kp: 7.1, imdb: 6.8, dur: '2 ч 10 мин', mins: 130, q4k: true,
    grad: ['#232526', '#914a2c'],
    desc: 'Охранник инкассаторского поезда понимает, что ограбление готовит кто-то из экипажа — и до конечной станции осталось шесть часов.',
    cast: ['Данила Крепкий', 'Мила Ворон', 'Эдгар Саар'],
  },
  {
    id: 'saturn', name: 'Под луной Сатурна', type: 'movie', year: 2024,
    genres: ['мелодрама', 'фантастика'], kp: 7.6, imdb: 7.2, dur: '1 ч 47 мин', mins: 107, q4k: false,
    grad: ['#355c7d', '#c06c84'],
    desc: 'Астроном на орбитальной станции и диктор ночного радио на Земле ведут разговор, который длится дольше, чем позволяет скорость света.',
    cast: ['Арина Светлова', 'Лев Кандауров'],
  },
  {
    id: 'empire', name: 'Империя теней', type: 'serial', year: 2024,
    genres: ['фэнтези', 'приключения'], kp: 8.6, imdb: 8.4, dur: '2 сезона', q4k: true,
    grad: ['#2c003e', '#907ad6'],
    desc: 'Наследница свергнутой династии возвращается в столицу под чужим именем, чтобы собрать армию из тех, кого империя предпочла забыть.',
    cast: ['Милана Артова', 'Казимир Вельд', 'Ольга Тур', 'Ян Пресс'],
  },
  {
    id: 'dept44', name: 'Отдел 44', type: 'serial', year: 2025,
    genres: ['криминал', 'детектив'], kp: 7.7, imdb: 7.5, dur: '1 сезон', q4k: false,
    grad: ['#14213d', '#fca311'],
    desc: 'Отдел по «висякам» получает нового руководителя и первое за десять лет дело, которое никто в городе не хочет раскрывать.',
    cast: ['Инна Рокотова', 'Фёдор Данин', 'Руслан Кейт'],
  },
  {
    id: 'school', name: 'Школа на холме', type: 'serial', year: 2023,
    genres: ['комедия', 'семейный'], kp: 7.2, imdb: 6.9, dur: '3 сезона', q4k: false,
    grad: ['#005f73', '#94d2bd'],
    desc: 'Молодой учитель литературы приезжает в посёлок, где школа стоит на холме, а все сплетни разлетаются быстрее школьного звонка.',
    cast: ['Соня Берг', 'Тихон Лапин', 'Вера Ладо'],
  },
];

const COLLECTIONS = [
  { name: 'Премия «Золотой экран» — номинанты', count: '12 фильмов', grad: ['#3c1053', '#ad5389'] },
  { name: 'Киберпанк-вечер', count: '8 фильмов и сериалов', grad: ['#0f2027', '#2c5364'] },
  { name: 'Семейный уикенд', count: '15 фильмов', grad: ['#134e5e', '#71b280'] },
  { name: 'Тёмный детектив', count: '10 сериалов', grad: ['#141e30', '#5a3d55'] },
];

const NAV = [
  ['search', 'Поиск'], ['home', 'Главная'], ['movies', 'Фильмы'], ['serials', 'Сериалы'],
  ['tv', 'ТВ'], ['bookmarks', 'Закладки'], ['settings', 'Настройки'],
];

const POPUPS = {
  audio:   { title: 'Аудиодорожка', key: 'audio',   items: ['Русский', 'English', 'Украинский'] },
  subs:    { title: 'Субтитры',     key: 'subs',    items: ['Выкл', 'Русские', 'Английские'] },
  quality: { title: 'Качество',     key: 'quality', items: ['Авто', '4K', '1080p', '720p'] },
};

/* ---------------------------- Состояние --------------------------------- */

const FEATURED = TITLES[0];
const CONTINUE = TITLES.filter(t => t.progress);
const NEW_MOVIES = TITLES.filter(t => t.type === 'movie');
const SERIALS = TITLES.filter(t => t.type === 'serial');

const ROWS = { home: [], detail: [], player: [] };
const FOCUS = { home: { r: 1, c: 0 }, detail: { r: 0, c: 0 }, player: { r: 0, c: 1 } };

const state = {
  screen: 'home',
  prev: 'home',
  title: null,
  season: 0,
  episode: 0,
  playing: false,
  time: 0,
  duration: 90 * 60,
  audio: 'Русский',
  subs: 'Выкл',
  quality: 'Авто',
  popup: null,
  popupIdx: 0,
};

/* ----------------------------- Хелперы ---------------------------------- */

const $ = s => document.querySelector(s);
const byId = id => TITLES.find(t => t.id === id);
const grad = (t, a = 160) => `linear-gradient(${a}deg, ${t.grad[0]}, ${t.grad[1]})`;

function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}

function fmtTime(sec) {
  sec = Math.max(0, Math.floor(sec));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  const mm = h ? String(m).padStart(2, '0') : String(m);
  return (h ? h + ':' : '') + mm + ':' + String(s).padStart(2, '0');
}

function kpClass(t) { return t.kp >= 7.5 ? 'good' : t.kp >= 6 ? 'mid' : 'low'; }

function leftText(t) {
  if (t.type === 'serial') return `Сезон ${t.progress.s + 1} · Серия ${t.progress.e + 1}`;
  const left = Math.round((1 - t.progress.pos) * t.mins);
  const h = Math.floor(left / 60), m = left % 60;
  return 'осталось ' + (h ? `${h} ч ${m} мин` : `${m} мин`);
}

function ensureSeasons(t) {
  if (t.type !== 'serial') return;
  if (!t.seasons) {
    const count = t.dur.includes('2') ? 2 : 1;
    t.seasons = Array.from({ length: count }, (_, si) => ({
      name: 'Сезон ' + (si + 1),
      episodes: Array.from({ length: 8 }, (_, i) => ({
        n: i + 1, name: 'Серия ' + (i + 1), dur: (44 + ((i * 7) % 11)) + ' мин', watched: false,
      })),
    }));
  }
}

let toastTimer = null;
function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), 2600);
}

/* --------------------------- Карточки/рельсы ----------------------------- */

function posterCard(t) {
  const c = el('div', 'card focusable');
  c.dataset.kind = 'title';
  c.dataset.id = t.id;
  c.innerHTML = `
    <div class="poster-art" style="background:${grad(t)}">
      ${t.q4k ? '<div class="badge4k">4K</div>' : ''}
      <div class="poster-name">${t.name}</div>
    </div>
    <div class="card-sub">${t.year} · ★ <b>${t.kp.toFixed(1)}</b></div>`;
  return c;
}

function continueCard(t) {
  const c = el('div', 'card focusable');
  c.dataset.kind = 'watch';
  c.dataset.id = t.id;
  c.innerHTML = `
    <div class="cw-art" style="background:${grad(t, 140)}">
      <div class="cw-play">▶</div>
      <div class="cw-name">${t.name}</div>
      <div class="cw-progress"><i style="width:${Math.round(t.progress.pos * 100)}%"></i></div>
    </div>
    <div class="card-sub">${leftText(t)}</div>`;
  return c;
}

function collectionCard(col) {
  const c = el('div', 'card focusable');
  c.dataset.kind = 'collection';
  c.dataset.name = col.name;
  c.innerHTML = `
    <div class="col-art" style="background:linear-gradient(130deg, ${col.grad[0]}, ${col.grad[1]})">
      <div class="col-name">${col.name}</div>
      <div class="col-count">${col.count}</div>
    </div>`;
  return c;
}

function rail(title, cards, cls) {
  const r = el('section', 'rail vrow' + (cls ? ' ' + cls : ''));
  r.appendChild(el('h2', null, title));
  const track = el('div', 'track');
  cards.forEach(c => track.appendChild(c));
  r.appendChild(track);
  return r;
}

/* ------------------------------- Главная -------------------------------- */

function renderNav() {
  const nav = $('#topnav');
  nav.innerHTML = '<div class="nav-logo"><b>KP</b>·KinoPub</div>';
  NAV.forEach(([id, label]) => {
    const item = el('div', 'nav-item focusable' + (id === 'home' ? ' current' : ''), label);
    item.dataset.nav = id;
    nav.appendChild(item);
  });
  nav.appendChild(el('div', 'nav-spacer'));
  const av = el('div', 'nav-avatar focusable', 'А');
  av.dataset.nav = 'profile';
  nav.appendChild(av);
}

function renderHome() {
  renderNav();
  const c = $('#home-content');
  c.innerHTML = '';
  c.style.transform = 'translateY(0)';

  const f = FEATURED;
  const hero = el('section', 'hero vrow');
  hero.innerHTML = `
    <div class="hero-bg" style="background:${grad(f, 115)}"></div>
    <div class="hero-fade"></div>
    <div class="hero-info">
      <div class="hero-tag">Фильм · Премьера недели</div>
      <h1>${f.name}</h1>
      <div class="meta">
        <span class="rate kp ${kpClass(f)}">${f.kp.toFixed(1)}</span>
        <span class="rate imdb">IMDb ${f.imdb.toFixed(1)}</span>
        <span>${f.year}</span>
        <span>${f.genres.join(' · ')}</span>
        <span>${f.dur}</span>
        ${f.q4k ? '<span class="uhd">4K</span>' : ''}
      </div>
      <p class="hero-desc">${f.desc}</p>
      <div class="hero-btns">
        <button class="btn primary focusable" data-act="watch">▶ Смотреть</button>
        <button class="btn focusable" data-act="more">Подробнее</button>
      </div>
    </div>`;
  c.appendChild(hero);

  c.appendChild(rail('Продолжить просмотр', CONTINUE.map(continueCard)));
  c.appendChild(rail('Новинки', NEW_MOVIES.map(posterCard)));
  c.appendChild(rail('Популярные сериалы', SERIALS.map(posterCard)));
  c.appendChild(rail('Подборки', COLLECTIONS.map(collectionCard)));

  buildHomeRows();
}

function buildHomeRows() {
  ROWS.home = [
    [...document.querySelectorAll('#topnav .focusable')],
    [...document.querySelectorAll('.hero-btns .btn')],
    ...[...document.querySelectorAll('#home-content .rail')].map(r => [...r.querySelectorAll('.card')]),
  ];
}

/* --------------------------- Детальная страница -------------------------- */

function epCard(t, e) {
  const c = el('div', 'card ep focusable');
  c.dataset.s = state.season;
  c.dataset.e = e.n - 1;
  c.innerHTML = `
    <div class="ep-art" style="background:${grad(t, 200)}">
      <span class="ep-num">${e.n}</span>
      ${e.watched ? '<span class="ep-done">✓</span>' : ''}
    </div>
    <div class="card-title">${e.n}. ${e.name}</div>
    <div class="card-sub">${e.dur}</div>`;
  return c;
}

function renderDetail() {
  const t = state.title;
  ensureSeasons(t);
  const s = $('#screen-detail');
  s.innerHTML = `
    <div class="detail-backdrop" style="background:${grad(t, 120)}"></div>
    <div class="detail-fade"></div>
    <div id="detail-scroll"><div id="detail-content" class="scroll-content"></div></div>`;
  const c = $('#detail-content');

  const main = el('section', 'detail-main vrow');
  main.innerHTML = `
    <div class="d-poster" style="background:${grad(t)}"><div class="poster-name">${t.name}</div></div>
    <div class="d-info">
      <div class="detail-back">Backspace — назад</div>
      <h1>${t.name}</h1>
      <div class="meta">
        <span class="rate kp ${kpClass(t)}">КиноПаб ${t.kp.toFixed(1)}</span>
        <span class="rate imdb">IMDb ${t.imdb.toFixed(1)}</span>
        <span>${t.year}</span>
        <span>${t.genres.join(' · ')}</span>
        <span>${t.dur}</span>
        ${t.q4k ? '<span class="uhd">4K</span>' : ''}
      </div>
      <div class="d-btns">
        <button class="btn primary focusable" data-act="watch">▶ Смотреть</button>
        <button class="btn focusable" data-act="trailer">Трейлер</button>
        <button class="btn focusable" data-act="later"><span class="b-txt">Буду смотреть</span></button>
        <button class="btn focusable" data-act="bookmark"><span class="b-txt">В закладки</span></button>
      </div>
      <p class="d-desc">${t.desc}</p>
      <div class="d-cast"><span class="cast-label">В ролях:</span>${t.cast.map(a => `<span class="actor">${a}</span>`).join('')}</div>
    </div>`;
  c.appendChild(main);

  if (t.type === 'serial') {
    const sec = el('section', 'rail d-seasons vrow');
    sec.style.marginLeft = '72px';
    const tabs = el('div', 'tabs');
    t.seasons.forEach((se, i) => {
      const tab = el('div', 'tab focusable' + (i === state.season ? ' active' : ''), se.name);
      tab.dataset.season = i;
      tabs.appendChild(tab);
    });
    sec.appendChild(tabs);
    const track = el('div', 'track');
    t.seasons[state.season].episodes.forEach(e => track.appendChild(epCard(t, e)));
    sec.appendChild(track);
    c.appendChild(sec);
  }

  const similar = TITLES.filter(x => x.id !== t.id && x.type === t.type).slice(0, 6);
  c.appendChild(rail('Похожие', similar.map(posterCard), 'similar'));

  buildDetailRows();
}

function buildDetailRows() {
  ROWS.detail = [
    [...document.querySelectorAll('#detail-content .d-btns .btn')],
  ];
  if (state.title.type === 'serial') {
    ROWS.detail.push([...document.querySelectorAll('#detail-content .tab')]);
    ROWS.detail.push([...document.querySelectorAll('.d-seasons .card')]);
  }
  ROWS.detail.push([...document.querySelectorAll('#detail-content .similar .card')]);
}

function seasonSelect(i) {
  state.season = i;
  renderDetail();
  FOCUS.detail = { r: 1, c: i };
  applyFocus();
}

/* -------------------------------- Плеер ---------------------------------- */

const CONTROLS = [
  ['rew', '−10 c'], ['play', '▶'], ['fwd', '+10 c'],
  ['audio', ''], ['subs', ''], ['quality', ''], ['next', 'След. серия ⏭'],
];

function buildPlayer() {
  const bar = $('#player-controls');
  bar.innerHTML = '';
  CONTROLS.forEach(([id, txt]) => {
    const b = el('button', 'pbtn focusable', txt);
    b.dataset.c = id;
    bar.appendChild(b);
  });
  ROWS.player = [[...bar.querySelectorAll('.pbtn')]];
}

function setCtl(id, txt) {
  const b = document.querySelector(`.pbtn[data-c="${id}"]`);
  if (b) b.textContent = txt;
}

function updatePlayerUI() {
  const t = state.title;
  $('#player-video').style.background = grad(t, 135);
  $('#pv-title').textContent = t.name;
  $('#pv-ep').textContent = t.type === 'serial'
    ? `${t.seasons[state.season].name} · Серия ${state.episode + 1} «${t.seasons[state.season].episodes[state.episode].name}»`
    : `${t.year} · ${t.genres.join(' · ')}`;
  $('#pp-total').textContent = fmtTime(state.duration);
  updateProgress();
  updateControlLabels();
}

function updateControlLabels() {
  setCtl('play', state.playing ? '❚❚' : '▶');
  setCtl('audio', 'Аудио · ' + state.audio);
  setCtl('subs', 'Субтитры · ' + state.subs);
  setCtl('quality', 'Качество · ' + state.quality);
  $('#player-paused').classList.toggle('hidden', state.playing);
}

function updateProgress() {
  $('#pp-fill').style.width = (state.duration ? (state.time / state.duration) * 100 : 0) + '%';
  $('#pp-cur').textContent = fmtTime(state.time);
}

function openPlayer(id, sIdx, eIdx) {
  const t = byId(id);
  ensureSeasons(t);
  state.prev = state.screen === 'player' ? state.prev : state.screen;
  state.title = t;
  const resume = sIdx === undefined && t.progress;
  if (t.type === 'serial') {
    state.season = sIdx !== undefined ? sIdx : (t.progress ? t.progress.s : 0);
    state.episode = eIdx !== undefined ? eIdx : (t.progress ? t.progress.e : 0);
    state.duration = 52 * 60;
  } else {
    state.season = 0;
    state.episode = 0;
    state.duration = t.mins * 60;
  }
  state.time = resume ? Math.floor(t.progress.pos * state.duration) : 0;
  state.playing = true;
  state.popup = null;
  $('#player-popup').classList.add('hidden');
  FOCUS.player.c = 1;
  updatePlayerUI();
  switchScreen('player');
  showOverlay();
}

let hideTimer = null;
function showOverlay() {
  $('#player-overlay').classList.add('visible');
  clearTimeout(hideTimer);
  hideTimer = setTimeout(() => {
    if (!state.popup) $('#player-overlay').classList.remove('visible');
  }, 3500);
}

function openPopup(kind) {
  state.popup = kind;
  const cfg = POPUPS[kind];
  state.popupIdx = Math.max(0, cfg.items.indexOf(state[cfg.key]));
  renderPopup();
}

function renderPopup() {
  const cfg = POPUPS[state.popup];
  const p = $('#player-popup');
  p.innerHTML = `<div class="popup-title">${cfg.title}</div>` + cfg.items.map((it, i) =>
    `<div class="popup-item${state[cfg.key] === it ? ' sel' : ''}${i === state.popupIdx ? ' cur' : ''}" data-i="${i}">${it}${state[cfg.key] === it ? ' ✓' : ''}</div>`
  ).join('');
  p.classList.remove('hidden');
}

function selectPopup(i) {
  const cfg = POPUPS[state.popup];
  state[cfg.key] = cfg.items[i];
  toast(`${cfg.title}: ${cfg.items[i]}`);
  closePopup();
  updateControlLabels();
}

function closePopup() {
  state.popup = null;
  $('#player-popup').classList.add('hidden');
  showOverlay();
}

function nextEpisode() {
  const t = state.title;
  if (t.type !== 'serial') { toast('Это фильм — следующей серии нет'); return; }
  let s = state.season, e = state.episode + 1;
  if (e >= t.seasons[s].episodes.length) { s++; e = 0; }
  if (s >= t.seasons.length) { toast('Это последняя серия'); return; }
  state.season = s; state.episode = e; state.time = 0; state.playing = true;
  updatePlayerUI();
  toast(`Серия ${e + 1}: «${t.seasons[s].episodes[e].name}»`);
}

function activateControl(id) {
  if (id === 'rew') state.time = Math.max(0, state.time - 10);
  else if (id === 'fwd') state.time = Math.min(state.duration, state.time + 10);
  else if (id === 'play') { state.playing = !state.playing; updateControlLabels(); }
  else if (id === 'next') nextEpisode();
  else if (POPUPS[id]) openPopup(id);
  updateProgress();
}

/* --------------------------- Навигация и фокус --------------------------- */

function offsetTopIn(node, stop) {
  let y = 0;
  while (node && node !== stop) { y += node.offsetTop; node = node.offsetParent; }
  return y;
}

function applyFocus() {
  const scr = state.screen;
  const rows = ROWS[scr], f = FOCUS[scr];
  const screenEl = $('#screen-' + scr);
  screenEl.querySelectorAll('.focused').forEach(x => x.classList.remove('focused'));
  const row = rows[f.r];
  if (!row || !row.length) return;
  f.c = Math.max(0, Math.min(f.c, row.length - 1));
  const elm = row[f.c];
  elm.classList.add('focused');
  if (scr === 'player') return;

  // Вертикальный скролл страницы
  const content = screenEl.querySelector('.scroll-content');
  if (content) {
    const vrow = elm.closest('.vrow');
    const top = vrow ? offsetTopIn(vrow, content) : 0;
    const y = Math.max(0, Math.min(top - 200, content.scrollHeight - 1080));
    content.style.transform = `translateY(${-y}px)`;
  }
  // Горизонтальный скролл рельсы
  const track = elm.closest('.track');
  if (track) {
    const max = Math.max(0, track.scrollWidth - 1780);
    const shift = Math.max(0, Math.min(elm.offsetLeft - 24, max));
    track.style.transform = `translateX(${-shift}px)`;
  }
}

function move(dx, dy) {
  const rows = ROWS[state.screen], f = FOCUS[state.screen];
  if (!rows.length) return;
  if (dy) {
    const r = f.r + dy;
    if (r < 0 || r >= rows.length) return;
    f.r = r;
    f.c = Math.min(f.c, rows[r].length - 1);
  } else if (dx) {
    const c = f.c + dx;
    if (c < 0 || c >= rows[f.r].length) return;
    f.c = c;
  }
  applyFocus();
}

function switchScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
  $('#screen-' + name).classList.remove('hidden');
  state.screen = name;
  applyFocus();
}

function openDetail(id) {
  state.prev = state.screen;
  state.title = byId(id);
  state.season = 0;
  renderDetail();
  FOCUS.detail = { r: 0, c: 0 };
  switchScreen('detail');
}

function goBack() {
  if (state.screen === 'home') return;
  if (state.screen === 'player') {
    state.playing = false;
    switchScreen(state.prev === 'player' ? 'home' : state.prev);
  } else {
    switchScreen('home');
  }
}

/* ------------------------------ Активация -------------------------------- */

function navAction(id) {
  if (id === 'home') {
    FOCUS.home = { r: 1, c: 0 };
    applyFocus();
    return;
  }
  const names = Object.fromEntries(NAV);
  toast(id === 'profile'
    ? 'Профиль — в прототипе недоступен'
    : `Раздел «${names[id]}» — прототип показывает только главную, карточку и плеер`);
}

function activate() {
  const rows = ROWS[state.screen], f = FOCUS[state.screen];
  const elm = rows[f.r] && rows[f.r][f.c];
  if (!elm) return;

  if (state.screen === 'home') {
    if (elm.dataset.nav) return navAction(elm.dataset.nav);
    if (elm.dataset.act === 'watch') return openPlayer(FEATURED.id);
    if (elm.dataset.act === 'more') return openDetail(FEATURED.id);
    if (elm.dataset.kind === 'watch') return openPlayer(elm.dataset.id);
    if (elm.dataset.kind === 'title') return openDetail(elm.dataset.id);
    if (elm.dataset.kind === 'collection') return toast(`Подборка «${elm.dataset.name}» — в прототипе не открывается`);
  }

  if (state.screen === 'detail') {
    const a = elm.dataset.act;
    if (a === 'watch') return openPlayer(state.title.id);
    if (a === 'trailer') return toast('Трейлер — в прототипе не воспроизводится');
    if (a === 'later' || a === 'bookmark') {
      elm.classList.toggle('on');
      const txt = elm.querySelector('.b-txt');
      const on = elm.classList.contains('on');
      if (a === 'later') txt.textContent = on ? '✓ Буду смотреть' : 'Буду смотреть';
      else txt.textContent = on ? '✓ В закладках' : 'В закладки';
      return toast(on ? 'Добавлено' : 'Убрано');
    }
    if (elm.dataset.season !== undefined) return seasonSelect(+elm.dataset.season);
    if (elm.dataset.e !== undefined) return openPlayer(state.title.id, +elm.dataset.s, +elm.dataset.e);
    if (elm.dataset.kind === 'title') return openDetail(elm.dataset.id);
  }
}

/* ------------------------------ Клавиатура ------------------------------- */

function playerKey(k, e) {
  if (state.popup) {
    const n = POPUPS[state.popup].items.length;
    if (k === 'ArrowUp') { state.popupIdx = Math.max(0, state.popupIdx - 1); renderPopup(); }
    else if (k === 'ArrowDown') { state.popupIdx = Math.min(n - 1, state.popupIdx + 1); renderPopup(); }
    else if (k === 'Enter') selectPopup(state.popupIdx);
    else if (k === 'Backspace' || k === 'Escape') closePopup();
    else return;
    e.preventDefault();
    return;
  }
  if (k === 'Backspace' || k === 'Escape') { goBack(); e.preventDefault(); return; }
  const vis = $('#player-overlay').classList.contains('visible');
  if (!vis) { showOverlay(); e.preventDefault(); return; }
  if (k === 'ArrowLeft') { FOCUS.player.c = Math.max(0, FOCUS.player.c - 1); applyFocus(); }
  else if (k === 'ArrowRight') { FOCUS.player.c = Math.min(ROWS.player[0].length - 1, FOCUS.player.c + 1); applyFocus(); }
  else if (k === 'Enter') activateControl(ROWS.player[0][FOCUS.player.c].dataset.c);
  else if (k === ' ') { activateControl('play'); }
  else return;
  showOverlay();
  e.preventDefault();
}

document.addEventListener('keydown', e => {
  const k = e.key;
  if (state.screen === 'player') return playerKey(k, e);
  if (k === 'ArrowLeft') move(-1, 0);
  else if (k === 'ArrowRight') move(1, 0);
  else if (k === 'ArrowUp') move(0, -1);
  else if (k === 'ArrowDown') move(0, 1);
  else if (k === 'Enter') activate();
  else if (k === 'Backspace' || k === 'Escape') goBack();
  else return;
  e.preventDefault();
});

/* -------------------------------- Мышь ----------------------------------- */

function locate(rows, node) {
  for (let r = 0; r < rows.length; r++) {
    const c = rows[r].indexOf(node);
    if (c >= 0) return { r, c };
  }
  return null;
}

$('#stage').addEventListener('mouseover', e => {
  if (state.popup) {
    const it = e.target.closest('.popup-item');
    if (it) { state.popupIdx = +it.dataset.i; renderPopup(); }
    return;
  }
  const f = e.target.closest('.focusable');
  if (!f || state.screen === 'player' && !$('#player-overlay').classList.contains('visible')) return;
  const pos = locate(ROWS[state.screen], f);
  if (pos) { FOCUS[state.screen].r = pos.r; FOCUS[state.screen].c = pos.c; applyFocus(); }
});

$('#stage').addEventListener('click', e => {
  if (state.screen === 'player') {
    if (state.popup) {
      const it = e.target.closest('.popup-item');
      if (it) selectPopup(+it.dataset.i);
      else closePopup();
      return;
    }
    const vis = $('#player-overlay').classList.contains('visible');
    const b = e.target.closest('.pbtn');
    if (b && vis) {
      FOCUS.player.c = ROWS.player[0].indexOf(b);
      applyFocus();
      activateControl(b.dataset.c);
    }
    showOverlay();
    return;
  }
  const f = e.target.closest('.focusable');
  if (!f) return;
  const pos = locate(ROWS[state.screen], f);
  if (pos) { FOCUS[state.screen].r = pos.r; FOCUS[state.screen].c = pos.c; applyFocus(); activate(); }
});

$('#screen-player').addEventListener('mousemove', () => {
  if (!state.popup) showOverlay();
});

/* ------------------------------ Масштаб ---------------------------------- */

function fit() {
  const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
  $('#stage').style.transform = `translate(-50%,-50%) scale(${s})`;
}
window.addEventListener('resize', fit);

/* ------------------------------- Часы ------------------------------------ */

setInterval(() => {
  if (state.playing && state.screen === 'player') {
    state.time = Math.min(state.duration, state.time + 1);
    updateProgress();
    if (state.time >= state.duration) {
      state.playing = false;
      updateControlLabels();
      toast('Просмотр завершён');
    }
  }
}, 1000);

/* -------------------------------- Init ----------------------------------- */

buildPlayer();
renderHome();
fit();
applyFocus();
