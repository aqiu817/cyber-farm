const state = {
  data: null,
  session: null,
};

const runtime = {
  autoTickSeconds: 0,
};

let autoTickTimer = null;
let autoTickInFlight = false;

const farmGridEl = document.getElementById("farmGrid");
const bodyEl = document.body;
const weatherFxEl = document.getElementById("weatherFx");
const dayChipEl = document.getElementById("dayChip");
const energyEl = document.getElementById("energy");
const cropsEl = document.getElementById("crops");
const waterEl = document.getElementById("water");
const coinsEl = document.getElementById("coins");
const ripeCountEl = document.getElementById("ripeCount");
const emptyCountEl = document.getElementById("emptyCount");
const warehouseCountEl = document.getElementById("warehouseCount");
const sellPriceEachEl = document.getElementById("sellPriceEach");
const seasonLabelEl = document.getElementById("seasonLabel");
const marketRateEl = document.getElementById("marketRate");
const sessionIdEl = document.getElementById("sessionId");
const weatherLabelEl = document.getElementById("weatherLabel");
const timeSlotEl = document.getElementById("timeSlot");
const weatherBoxEl = document.getElementById("weatherBox");
const weatherHintEl = document.getElementById("weatherHint");
const missionLabelEl = document.getElementById("missionLabel");
const missionProgressEl = document.getElementById("missionProgress");
const missionRewardEl = document.getElementById("missionReward");
const missionFillEl = document.getElementById("missionFill");
const claimRewardBtn = document.getElementById("claimRewardBtn");
const logEl = document.getElementById("log");
const selectedPlotNameEl = document.getElementById("selectedPlotName");
const selectedPlotDescEl = document.getElementById("selectedPlotDesc");
const selectedStageEl = document.getElementById("selectedStage");
const selectedMoistureEl = document.getElementById("selectedMoisture");
const selectedGrowthEl = document.getElementById("selectedGrowth");
const selectedSoilEl = document.getElementById("selectedSoil");
const selectedBoostEl = document.getElementById("selectedBoost");
const selectedCropSpriteEl = document.getElementById("selectedCropSprite");
const waterBtn = document.getElementById("waterBtn");
const harvestBtn = document.getElementById("harvestBtn");
const clearBtn = document.getElementById("clearBtn");
const tickBtn = document.getElementById("tickBtn");
const fertilizeBtn = document.getElementById("fertilizeBtn");
const upgradePlotBtn = document.getElementById("upgradePlotBtn");
const sellOneBtn = document.getElementById("sellOneBtn");
const sellAllBtn = document.getElementById("sellAllBtn");
const seedButtons = document.querySelectorAll(".seed-btn[data-seed]");
const bagEls = {
  turnip: document.getElementById("bagTurnip"),
  tomato: document.getElementById("bagTomato"),
  melon: document.getElementById("bagMelon"),
  corn: document.getElementById("bagCorn"),
};
const buyButtons = {
  turnip: document.getElementById("buyTurnipBtn"),
  tomato: document.getElementById("buyTomatoBtn"),
  melon: document.getElementById("buyMelonBtn"),
  corn: document.getElementById("buyCornBtn"),
};

function current() {
  return state.data;
}

function gameState() {
  return current().state;
}

function meta() {
  return current().meta || { weatherLabel: gameState().weather, seasonLabel: gameState().season, ticksPerDay: 4, sellPriceEach: 12 };
}

function plots() {
  return current().plots;
}

function seeds() {
  return current().seeds;
}

function getPlotStatus(plot) {
  if (!plot.seed) return { label: "空地", badge: "empty", description: "适合播种新作物" };
  if (plot.moisture < 30) return { label: "缺水", badge: "dry", description: "需要立刻浇水" };
  if (plot.growth >= seeds()[plot.seed].growTime) return { label: "成熟", badge: "ripe", description: "可以收获了" };
  return { label: "生长", badge: "grow", description: "正在稳定生长" };
}

function weatherHint(weather) {
  if (weather === "rainy") return "自然补水，生长更快";
  if (weather === "cloudy") return "水分蒸发慢，适合保湿";
  if (weather === "breezy") return "微风通气，作物状态稳定";
  return "阳光充足，适合稳步生长";
}

function timeClass(tick, ticksPerDay) {
  const ratio = tick / Math.max(ticksPerDay, 1);
  if (ratio < 0.34) return "morning";
  if (ratio < 0.67) return "evening";
  return "night";
}

function getStageFrame(plot) {
  if (!plot.seed) {
    return { x: -16, y: 0, empty: true, growthText: "0 / 0" };
  }

  const seed = seeds()[plot.seed];
  const frame = Math.min(Math.max(plot.growth, 1), seed.growTime);
  const baseColumn = seed.sprite.group === 0 ? 1 : 7;
  const x = -(baseColumn + (seed.growTime - frame)) * 16;
  const y = -seed.sprite.row * 16;
  return { x, y, empty: false, growthText: `${Math.min(plot.growth, seed.growTime)} / ${seed.growTime}` };
}

function applySprite(el, plot) {
  const frame = getStageFrame(plot);
  el.style.backgroundPosition = `${frame.x}px ${frame.y}px`;
  el.classList.toggle("empty", frame.empty);
}

async function apiGet(path) {
  const response = await fetch(path);
  return response.json();
}

async function apiPost(path, payload = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json();
}

function shortSession(session) {
  return session ? `${session.slice(0, 8)}...` : "loading";
}

async function syncState() {
  const data = await apiGet("/api/state");
  state.data = data.state;
  state.session = data.session;
  renderAll();
}

async function loadRuntimeConfig() {
  try {
    const data = await apiGet("/api/config");
    runtime.autoTickSeconds = Math.max(0, Number(data?.config?.autoTickSeconds || 0));
  } catch {
    runtime.autoTickSeconds = 0;
  }
}

function setLog(message) {
  logEl.textContent = message;
}

async function runApi(call) {
  const result = await call();
  if (result.state) {
    state.data = result.state;
    state.session = result.session || state.session;
    renderAll();
  }
  setLog(result.ok ? result.message : result.error);
}

function renderWorldState() {
  const gs = gameState();
  const mission = gs.mission;
  const weather = gs.weather;
  const ticksPerDay = meta().ticksPerDay;
  const progress = mission.target === 0 ? 0 : Math.round((mission.progress / mission.target) * 100);
  const timeMode = timeClass(gs.tickInDay, ticksPerDay);

  dayChipEl.textContent = `Neo Valley / Day ${gs.day}`;
  sessionIdEl.textContent = shortSession(state.session);
  weatherLabelEl.textContent = meta().weatherLabel;
  timeSlotEl.textContent = `${gs.tickInDay + 1} / ${ticksPerDay}`;
  weatherBoxEl.textContent = meta().weatherLabel;
  weatherHintEl.textContent = weatherHint(weather);
  missionLabelEl.textContent = mission.label;
  missionProgressEl.textContent = `${mission.progress} / ${mission.target}`;
  missionRewardEl.textContent = `${mission.reward.coins} 金币 / ${mission.reward.energy} 能量`;
  missionFillEl.style.width = `${progress}%`;
  claimRewardBtn.disabled = mission.claimed || mission.progress < mission.target;
  claimRewardBtn.textContent = mission.claimed ? "奖励已领取" : "领取奖励";
  seasonLabelEl.textContent = meta().seasonLabel;
  marketRateEl.textContent = `x${Number(gs.marketRate || 1).toFixed(2)}`;
  sellPriceEachEl.textContent = `${meta().sellPriceEach} 金币`;

  weatherFxEl.className = `weather-fx ${weather}`;
  bodyEl.classList.remove("time-morning", "time-evening", "time-night");
  bodyEl.classList.add(`time-${timeMode}`);
}

function renderStats() {
  energyEl.textContent = gameState().energy;
  cropsEl.textContent = gameState().crops;
  waterEl.textContent = `${gameState().water}%`;
  coinsEl.textContent = gameState().coins;
  warehouseCountEl.textContent = gameState().warehouse;
  ripeCountEl.textContent = plots().filter((plot) => getPlotStatus(plot).badge === "ripe").length;
  emptyCountEl.textContent = plots().filter((plot) => !plot.seed).length;

  Object.entries(bagEls).forEach(([key, el]) => {
    el.textContent = gameState().inventory[key];
  });
}

function renderSelectedPlot() {
  const plot = plots()[gameState().selectedPlot];
  const status = getPlotStatus(plot);
  const seed = plot.seed ? seeds()[plot.seed] : null;
  const frame = getStageFrame(plot);

  selectedPlotNameEl.textContent = `${gameState().selectedPlot + 1}号地`;
  selectedPlotDescEl.textContent = seed ? `${seed.label}，${status.description}` : "空地已翻好，可以选择任意种子开始播种。";
  selectedStageEl.textContent = `状态: ${status.label}`;
  selectedMoistureEl.textContent = `湿度: ${plot.moisture}%`;
  selectedGrowthEl.textContent = `阶段: ${frame.growthText}`;
  selectedSoilEl.textContent = `土地等级: Lv.${plot.soilLevel || 1}`;
  selectedBoostEl.textContent = `加成: ${plot.fertilized ? "已施肥" : "无"}`;
  applySprite(selectedCropSpriteEl, plot);
}

function renderGrid() {
  farmGridEl.innerHTML = "";

  plots().forEach((plot, index) => {
    const seed = plot.seed ? seeds()[plot.seed] : null;
    const status = getPlotStatus(plot);
    const frame = getStageFrame(plot);

    const tile = document.createElement("article");
    tile.className = `tile ${plot.seed ? "" : "empty-soil"} ${gameState().selectedPlot === index ? "selected" : ""} ${status.badge === "ripe" ? "ripe-glow" : ""}`.trim();
    tile.addEventListener("click", async () => {
      await runApi(() => apiPost("/api/select", { plot: index }));
    });

    const header = document.createElement("div");
    header.className = "tile-header";

    const name = document.createElement("span");
    name.textContent = `${index + 1}号地 Lv.${plot.soilLevel || 1}`;

    const badge = document.createElement("span");
    badge.className = `badge ${status.badge}`;
    badge.textContent = plot.fertilized && plot.seed ? `${status.label}+` : status.label;
    header.append(name, badge);

    const cropSprite = document.createElement("div");
    cropSprite.className = "crop-sprite";
    cropSprite.style.backgroundPosition = `${frame.x}px ${frame.y}px`;
    cropSprite.classList.toggle("empty", frame.empty);

    const footer = document.createElement("div");
    footer.className = "tile-footer";

    const meta = document.createElement("span");
    meta.className = "tile-meta";
    meta.textContent = seed ? `${seed.label} ${frame.growthText}` : plot.fertilized ? "空地 / 已施肥" : "待播种";

    const waterBar = document.createElement("div");
    waterBar.className = "water-bar";

    const waterFill = document.createElement("div");
    waterFill.className = "water-fill";
    waterFill.style.width = `${plot.moisture}%`;
    waterBar.appendChild(waterFill);

    footer.append(meta, waterBar);
    tile.append(header, cropSprite, footer);
    farmGridEl.appendChild(tile);
  });
}

function renderAll() {
  if (!state.data) {
    return;
  }
  renderWorldState();
  renderStats();
  renderGrid();
  renderSelectedPlot();
}

seedButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    await runApi(() => apiPost("/api/action", { type: "plant", seed: button.dataset.seed }));
  });
});

Object.entries(buyButtons).forEach(([seedKey, button]) => {
  button.addEventListener("click", async () => {
    await runApi(() => apiPost("/api/action", { type: "buy", seed: seedKey }));
  });
});

waterBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "water" }));
});

harvestBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "harvest" }));
});

clearBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "clear" }));
});

tickBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/tick"));
});

fertilizeBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "fertilize" }));
});

upgradePlotBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "upgrade_plot" }));
});

claimRewardBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "claim_reward" }));
});

sellOneBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "sell", amount: 1 }));
});

sellAllBtn.addEventListener("click", async () => {
  await runApi(() => apiPost("/api/action", { type: "sell", amount: gameState().warehouse }));
});

window.cyberFarm = {
  getState: () => apiGet("/api/state"),
  select: (plot) => apiPost("/api/select", { plot }),
  plant: (seed) => apiPost("/api/action", { type: "plant", seed }),
  water: () => apiPost("/api/action", { type: "water" }),
  harvest: () => apiPost("/api/action", { type: "harvest" }),
  clear: () => apiPost("/api/action", { type: "clear" }),
  fertilize: () => apiPost("/api/action", { type: "fertilize" }),
  upgradePlot: () => apiPost("/api/action", { type: "upgrade_plot" }),
  buy: (seed) => apiPost("/api/action", { type: "buy", seed }),
  sell: (amount = 1) => apiPost("/api/action", { type: "sell", amount }),
  tick: () => apiPost("/api/tick"),
  claimReward: () => apiPost("/api/action", { type: "claim_reward" }),
  reset: () => apiPost("/api/reset"),
  sync: syncState,
};

async function boot() {
  await loadRuntimeConfig();
  await syncState();

  if (runtime.autoTickSeconds > 0) {
    autoTickTimer = setInterval(async () => {
      if (autoTickInFlight) {
        return;
      }
      autoTickInFlight = true;
      try {
        await runApi(() => apiPost("/api/tick"));
      } finally {
        autoTickInFlight = false;
      }
    }, runtime.autoTickSeconds * 1000);
  }
}

boot();
