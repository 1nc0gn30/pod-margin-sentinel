/**
 * POD Margin Sentinel - Kinetic Hero Canvas ("The Sovereign Margin Chronometer")
 * Pure HTML5 Canvas 60fps interactive financial visualizer with zero external dependencies.
 */

(function () {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let width, height;
  let mouse = { x: -1000, y: -1000, active: false };

  // Floating currency & percentage particles
  const PARTICLES = [];
  const PARTICLE_COUNT = 30;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = Math.max(300, rect.height || 380);
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    PARTICLES.push({
      x: Math.random(),
      y: Math.random(),
      size: 1.5 + Math.random() * 2.5,
      vx: (Math.random() - 0.5) * 0.0008,
      vy: (Math.random() - 0.5) * 0.0008,
      color: Math.random() > 0.5 ? "#FFDF70" : (Math.random() > 0.25 ? "#10B981" : "#38BDF8")
    });
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    const time = performance.now() * 0.001;
    const centerX = width > 800 ? width * 0.70 : width * 0.5;
    const centerY = height * 0.5;

    // Subtle financial coordinate grid
    ctx.save();
    ctx.strokeStyle = "rgba(255, 255, 255, 0.025)";
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    ctx.restore();

    // Floating particles
    ctx.save();
    for (let p of PARTICLES) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = 1;
      if (p.x > 1) p.x = 0;
      if (p.y < 0) p.y = 1;
      if (p.y > 1) p.y = 0;

      ctx.fillStyle = p.color;
      ctx.globalAlpha = 0.35;
      ctx.beginPath();
      ctx.arc(p.x * width, p.y * height, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    // Kinetic Chronometer Gauge Assembly
    ctx.save();
    ctx.translate(centerX, centerY);

    // Mouse tilt interaction
    if (mouse.active) {
      const dx = (mouse.x - centerX) * 0.0002;
      ctx.rotate(dx);
    }

    // Outer Calibrated Ring
    ctx.save();
    ctx.strokeStyle = "rgba(229, 169, 60, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 8]);
    ctx.beginPath();
    ctx.arc(0, 0, 130, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Concentric Waterfall Donut Rings
    // Ring 1: COGS Base (45%)
    ctx.save();
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(0, 0, 105, 0, Math.PI * 0.9);
    ctx.stroke();

    // Ring 2: Platform Fees (15%)
    ctx.strokeStyle = "#EF4444";
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(0, 0, 105, Math.PI * 0.9, Math.PI * 1.25);
    ctx.stroke();

    // Ring 3: Net Profit (40% Golden Margin)
    const sweep = Math.PI * (1.25 + (Math.sin(time * 1.5) * 0.05 + 0.70));
    ctx.strokeStyle = "#10B981";
    ctx.lineWidth = 9;
    ctx.beginPath();
    ctx.arc(0, 0, 105, Math.PI * 1.25, Math.min(Math.PI * 2, sweep));
    ctx.stroke();
    ctx.restore();

    // Inner Glowing Core
    const coreGrad = ctx.createRadialGradient(0, 0, 10, 0, 0, 75);
    coreGrad.addColorStop(0, "rgba(229, 169, 60, 0.2)");
    coreGrad.addColorStop(0.7, "rgba(16, 185, 129, 0.08)");
    coreGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(0, 0, 75, 0, Math.PI * 2);
    ctx.fill();

    // Rotating Sentinel Needle
    ctx.save();
    const needleAngle = -Math.PI / 4 + (Math.sin(time * 2) * 0.2 + 0.4);
    ctx.rotate(needleAngle);
    ctx.strokeStyle = "#FFDF70";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, -90);
    ctx.stroke();

    // Needle Tip
    ctx.fillStyle = "#10B981";
    ctx.beginPath();
    ctx.arc(0, -90, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Center Hub
    ctx.fillStyle = "#0F172A";
    ctx.strokeStyle = "#FFDF70";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.restore();

    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  window.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.active = true;
  });
  window.addEventListener("mouseleave", () => {
    mouse.active = false;
  });

  resize();
  requestAnimationFrame(draw);
})();
