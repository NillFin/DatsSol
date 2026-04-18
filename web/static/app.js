const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let tileSize = 30;

const ws = new WebSocket("ws://" + location.host + "/ws");

ws.onmessage = (event) => {
    const state = JSON.parse(event.data);
    render(state);
};

function render(state) {
    const main = state.plantations.find(p => p.isMain);
    if (!main) return;

    const worldWidth = state.size[0];
    const worldHeight = state.size[1];

    const vrTier = state.plantationUpgrades?.tiers?.find(
        t => t.name === "vision_range"
    );

    const baseVision = 3;
    const upgradeVision = vrTier?.current ?? 0;
    const visionRange = baseVision + upgradeVision;
    const cameraRadius = visionRange * 3;

    const centerX = main.position[0];
    const centerY = main.position[1];

    // ✅ clamp к границам карты
    let minX = Math.max(0, centerX - cameraRadius);
    let maxX = Math.min(worldWidth - 1, centerX + cameraRadius);
    let minY = Math.max(0, centerY - cameraRadius);
    let maxY = Math.min(worldHeight - 1, centerY + cameraRadius);

    const width = maxX - minX + 1;
    const height = maxY - minY + 1;

    console.log(minX, maxX, minY, maxY);

    canvas.width = width * tileSize;
    canvas.height = height * tileSize;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBackground();
    drawGrid(minX, minY, maxX, maxY);
    drawAxes(minX, minY, maxX, maxY);
    drawCells(state, minX, minY, maxX, maxY);
    drawBoostedStars(minX, minY, maxX, maxY);
    drawMountains(state, minX, minY, maxX, maxY);
    drawPlantations(state, minX, minY, maxX, maxY);
    drawEnemies(state, minX, minY, maxX, maxY);
    drawBeavers(state, minX, minY, maxX, maxY);
    drawConstruction(state, minX, minY, maxX, maxY);

    drawBorder();
    drawHUD(state);
}

function worldToScreen(x, y, minX, minY, maxY) {
    const screenX = (x - minX) * tileSize;
    const screenY = (maxY - y) * tileSize;
    return [screenX, screenY];
}

function drawBackground() {
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawGrid(minX, minY, maxX, maxY) {
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;

    const width = maxX - minX + 1;
    const height = maxY - minY + 1;

    // вертикальные линии
    for (let i = 0; i <= width; i++) {
        ctx.beginPath();
        ctx.moveTo(i * tileSize, 0);
        ctx.lineTo(i * tileSize, height * tileSize);
        ctx.stroke();
    }

    // горизонтальные линии
    for (let j = 0; j <= height; j++) {
        ctx.beginPath();
        ctx.moveTo(0, j * tileSize);
        ctx.lineTo(width * tileSize, j * tileSize);
        ctx.stroke();
    }
}

function drawAxes(minX, minY, maxX, maxY) {
    ctx.font = "10px monospace";

    const width = maxX - minX + 1;
    const height = maxY - minY + 1;

    // ✅ Подписи X
    for (let i = 0; i < width; i++) {
        const worldX = minX + i;

        const screenX = i * tileSize + tileSize / 2;

        if (worldX % 7 === 0) {
            ctx.fillStyle = "#ffd700"; // золотой
            ctx.font = "bold 11px monospace";
        } else {
            ctx.fillStyle = "rgba(255,255,255,0.6)";
            ctx.font = "10px monospace";
        }

        ctx.fillText(
            worldX,
            screenX - 8,
            12
        );
    }

    // ✅ Подписи Y
    for (let j = 0; j < height; j++) {
        const worldY = maxY - j;

        const screenY = j * tileSize + tileSize / 2 + 3;

        if (worldY % 7 === 0) {
            ctx.fillStyle = "#ffd700";
            ctx.font = "bold 11px monospace";
        } else {
            ctx.fillStyle = "rgba(255,255,255,0.6)";
            ctx.font = "10px monospace";
        }

        ctx.fillText(
            worldY,
            2,
            screenY
        );
    }
}

function drawCells(state, minX, minY, maxX, maxY) {
    if (!state.cells) return;

    for (const cell of state.cells) {
        const [x, y] = cell.position;

        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const progress = cell.terraformationProgress;
        const green = Math.floor(progress * 2);

        ctx.fillStyle = `rgb(0, ${green}, 0)`;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);

        ctx.fillRect(sx, sy, tileSize, tileSize);
    }
}

function drawBoostedStars(minX, minY, maxX, maxY) {
    ctx.fillStyle = "#ffd700";
    ctx.strokeStyle = "#ffcc00";
    ctx.lineWidth = 1;

    for (let x = minX; x <= maxX; x++) {
        for (let y = minY; y <= maxY; y++) {

            if (x % 7 === 0 && y % 7 === 0) {

                const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);

                drawStar(
                    sx + tileSize / 2,
                    sy + tileSize / 2,
                    tileSize / 4,
                    tileSize / 8,
                    5
                );
            }
        }
    }
}

function drawStar(cx, cy, outerRadius, innerRadius, points) {
    ctx.beginPath();

    for (let i = 0; i < points * 2; i++) {
        const angle = (Math.PI / points) * i;
        const radius = i % 2 === 0 ? outerRadius : innerRadius;

        const x = cx + Math.cos(angle - Math.PI / 2) * radius;
        const y = cy + Math.sin(angle - Math.PI / 2) * radius;

        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }

    ctx.closePath();
    ctx.fill();
}

function drawMountains(state, minX, minY, maxX, maxY) {
    if (!state.mountains) return;

    ctx.fillStyle = "#444";

    for (const m of state.mountains) {
        const [x, y] = m;
        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);

        ctx.fillRect(sx, sy, tileSize, tileSize);
    }
}

function drawPlantations(state, minX, minY, maxX, maxY) {
    if (!state.plantations) return;

    for (const p of state.plantations) {
        const [x, y] = p.position;
        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);

        ctx.fillStyle = p.isMain ? "cyan" : "blue";

        // ctx.fillRect(sx, sy, tileSize, tileSize);
        ctx.beginPath();
        ctx.arc(
            sx + tileSize / 2,
            sy + tileSize / 2,
            tileSize / 2,
            0,
            2 * Math.PI
        );
        ctx.fill();
    }
}

function drawEnemies(state, minX, minY, maxX, maxY) {
    if (!state.enemy) return;

    ctx.fillStyle = "red";

    for (const e of state.enemy) {
        const [x, y] = e.position;
        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);
        ctx.fillRect(sx, sy, tileSize, tileSize);
    }
}

function drawBeavers(state, minX, minY, maxX, maxY) {
    if (!state.beavers) return;

    ctx.fillStyle = "orange";

    for (const b of state.beavers) {
        const [x, y] = b.position;
        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);
        ctx.fillRect(sx, sy, tileSize, tileSize);
    }
}

function drawConstruction(state, minX, minY, maxX, maxY) {
    if (!state.construction) return;

    ctx.fillStyle = "yellow";

    for (const c of state.construction) {
        const [x, y] = c.position;
        if (x < minX || x > maxX || y < minY || y > maxY) continue;

        const [sx, sy] = worldToScreen(x, y, minX, minY, maxY);
        ctx.fillRect(sx, sy, tileSize, tileSize);
    }
}

function drawBorder() {
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
}

function drawHUD(state) {
    ctx.fillStyle = "white";
    ctx.font = "14px monospace";

    const r = state.roundInfo;

    const round = r?.name ?? "N/A";
    const start = r?.startAt ? new Date(r.startAt).toLocaleTimeString() : "-";
    const end = r?.endAt ? new Date(r.endAt).toLocaleTimeString() : "-";

    const lines = [
        `Round: ${round}`,
        `Start: ${start}`,
        `End:   ${end}`,
        `Turn:  ${state.turnNo}`
    ];

    let y = 20;
    for (const line of lines) {
        ctx.fillText(line, 10, y);
        y += 18;
    }
}