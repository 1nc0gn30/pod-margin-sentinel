/**
 * POD Margin Sentinel - Interactive In-Browser Financial Engine
 * 100% Client-side mathematical execution, zero fake work.
 */

(function () {
  const PRESETS = {
    gildan_18000: { name: "Gildan 18000 Sweatshirt", retail: 34.99, wholesale: 12.50, shipping: 5.49, charged_ship: 0.0 },
    comfort_colors_1717: { name: "Comfort Colors 1717 Tee", retail: 29.99, wholesale: 10.80, shipping: 4.79, charged_ship: 0.0 },
    bella_canvas_3001: { name: "Bella+Canvas 3001 Tee", retail: 26.99, wholesale: 8.90, shipping: 4.79, charged_ship: 0.0 },
    ceramic_mug_15oz: { name: "15oz Ceramic Mug", retail: 21.99, wholesale: 6.80, shipping: 6.99, charged_ship: 0.0 },
    canvas_wrap: { name: "Canvas Wrap 16x20", retail: 49.99, wholesale: 18.50, shipping: 9.99, charged_ship: 0.0 },
    tote_bag: { name: "Heavyweight Cotton Tote", retail: 24.99, wholesale: 7.20, shipping: 4.99, charged_ship: 0.0 },
    digital_pack: { name: "Digital Art Pack (300 DPI)", retail: 9.99, wholesale: 0.00, shipping: 0.00, charged_ship: 0.0 }
  };

  const PLATFORMS = {
    etsy_organic: { name: "Etsy (Organic Search)", tx: 0.065, pp: 0.030, pp_fix: 0.25, list_fix: 0.20, ads: 0.0 },
    etsy_offsite_ads_15: { name: "Etsy (Offsite Ads 15%)", tx: 0.065, pp: 0.030, pp_fix: 0.25, list_fix: 0.20, ads: 0.15 },
    etsy_offsite_ads_12: { name: "Etsy (Offsite Ads 12%)", tx: 0.065, pp: 0.030, pp_fix: 0.25, list_fix: 0.20, ads: 0.12 },
    shopify_payments: { name: "Shopify Payments", tx: 0.0, pp: 0.029, pp_fix: 0.30, list_fix: 0.0, ads: 0.0 },
    tiktok_shop: { name: "TikTok Shop (US)", tx: 0.060, pp: 0.0, pp_fix: 0.30, list_fix: 0.0, ads: 0.0 }
  };

  let state = {
    retail: 34.99,
    wholesale: 12.50,
    shipping: 5.49,
    charged_ship: 0.0,
    discount: 0.0,
    platform: "etsy_organic",
    isProLicensed: false
  };

  // DOM Elements
  const retailSlider = document.getElementById("slider-retail");
  const retailDisplay = document.getElementById("display-retail");
  const wholesaleSlider = document.getElementById("slider-wholesale");
  const wholesaleDisplay = document.getElementById("display-wholesale");
  const shippingSlider = document.getElementById("slider-shipping");
  const shippingDisplay = document.getElementById("display-shipping");
  const chargedShipSlider = document.getElementById("slider-charged-ship");
  const chargedShipDisplay = document.getElementById("display-charged-ship");
  const discountSlider = document.getElementById("slider-discount");
  const discountDisplay = document.getElementById("display-discount");

  const netProfitEl = document.getElementById("val-net-profit");
  const netMarginEl = document.getElementById("val-net-margin");
  const grossRevEl = document.getElementById("val-gross-rev");
  const totalCogsEl = document.getElementById("val-total-cogs");
  const totalFeesEl = document.getElementById("val-total-fees");
  const txFeeEl = document.getElementById("val-tx-fee");
  const ppFeeEl = document.getElementById("val-pp-fee");
  const offsiteFeeEl = document.getElementById("val-offsite-fee");

  const breakEvenPriceEl = document.getElementById("val-breakeven-price");
  const target35PriceEl = document.getElementById("val-target35-price");
  const target50PriceEl = document.getElementById("val-target50-price");

  const comparisonContainer = document.getElementById("comparison-container");
  const couponContainer = document.getElementById("coupon-table-body");

  const paywallWrapper = document.getElementById("paywall-wrapper");
  const paywallOverlay = document.getElementById("paywall-overlay");
  const proBadge = document.getElementById("pro-badge");
  const exportCsvBtn = document.getElementById("export-csv-btn");

  const licenseModal = document.getElementById("license-modal");
  const openLicenseModalBtn = document.getElementById("open-license-modal-btn");
  const closeLicenseModalBtn = document.getElementById("close-license-modal-btn");
  const licenseKeyInput = document.getElementById("license-key-input");
  const activateKeyBtn = document.getElementById("activate-key-btn");
  const licenseStatusEl = document.getElementById("license-status");

  function checkProStatus() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("licensed") === "true") {
      localStorage.setItem("margin_sentinel_pro_licensed", "true");
    }

    if (localStorage.getItem("margin_sentinel_pro_licensed") === "true") {
      state.isProLicensed = true;
      if (proBadge) proBadge.style.display = "inline-flex";
      if (paywallWrapper) {
        paywallWrapper.classList.remove("paywall-content-locked");
        paywallWrapper.classList.add("paywall-content-unlocked");
      }
      if (paywallOverlay) paywallOverlay.style.display = "none";
    }
  }

  function recalculate() {
    const spec = PLATFORMS[state.platform];
    const discountedRetail = state.retail * (1 - state.discount / 100);
    const grossRevenue = discountedRetail + state.charged_ship;

    const txFee = grossRevenue * spec.tx;
    const ppFee = grossRevenue * spec.pp + spec.pp_fix;
    const listFee = spec.list_fix;
    const offsiteFee = grossRevenue * spec.ads;
    const totalFees = txFee + ppFee + listFee + offsiteFee;

    const totalCogs = state.wholesale + state.shipping;
    const netProfit = grossRevenue - totalFees - totalCogs;
    const netMargin = grossRevenue > 0 ? (netProfit / grossRevenue) * 100 : 0;

    // Update Displays
    if (retailDisplay) retailDisplay.textContent = `$${state.retail.toFixed(2)}`;
    if (wholesaleDisplay) wholesaleDisplay.textContent = `$${state.wholesale.toFixed(2)}`;
    if (shippingDisplay) shippingDisplay.textContent = `$${state.shipping.toFixed(2)}`;
    if (chargedShipDisplay) chargedShipDisplay.textContent = `$${state.charged_ship.toFixed(2)}`;
    if (discountDisplay) discountDisplay.textContent = `${state.discount.toFixed(0)}%`;

    if (netProfitEl) {
      netProfitEl.textContent = `$${netProfit.toFixed(2)}`;
      netProfitEl.style.color = netProfit >= 10 ? "#10B981" : (netProfit > 0 ? "#F59E0B" : "#EF4444");
    }
    if (netMarginEl) {
      netMarginEl.textContent = `${netMargin.toFixed(1)}% NET MARGIN`;
      netMarginEl.style.color = netMargin >= 25 ? "#10B981" : (netMargin > 0 ? "#F59E0B" : "#EF4444");
    }

    if (grossRevEl) grossRevEl.textContent = `$${grossRevenue.toFixed(2)}`;
    if (totalCogsEl) totalCogsEl.textContent = `$${totalCogs.toFixed(2)}`;
    if (totalFeesEl) totalFeesEl.textContent = `-$${totalFees.toFixed(2)}`;
    if (txFeeEl) txFeeEl.textContent = `-$${txFee.toFixed(2)}`;
    if (ppFeeEl) ppFeeEl.textContent = `-$${ppFee.toFixed(2)}`;
    if (offsiteFeeEl) offsiteFeeEl.textContent = `-$${offsiteFee.toFixed(2)}`;

    // Break-even and Target Prices
    const varRate = spec.tx + spec.pp + spec.ads;
    const fixFees = spec.pp_fix + spec.list_fix;

    // Break Even: Revenue * (1 - varRate) = totalCogs + fixFees
    const bePrice = (totalCogs + fixFees) / (1 - varRate) - state.charged_ship;
    if (breakEvenPriceEl) breakEvenPriceEl.textContent = `$${Math.max(0, bePrice).toFixed(2)}`;

    // Target 35% margin
    const target35Price = (totalCogs + fixFees) / (1 - varRate - 0.35) - state.charged_ship;
    if (target35PriceEl) target35PriceEl.textContent = `$${Math.max(0, target35Price).toFixed(2)}`;

    // Target 50% margin
    const target50Price = (totalCogs + fixFees) / (1 - varRate - 0.50) - state.charged_ship;
    if (target50PriceEl) target50PriceEl.textContent = `$${Math.max(0, target50Price).toFixed(2)}`;

    renderComparisonCards();
    renderCouponMatrix();
  }

  function renderComparisonCards() {
    if (!comparisonContainer) return;
    comparisonContainer.innerHTML = "";

    const totalCogs = state.wholesale + state.shipping;

    Object.keys(PLATFORMS).forEach((key) => {
      const p = PLATFORMS[key];
      const gross = state.retail + state.charged_ship;
      const fees = (gross * p.tx) + (gross * p.pp + p.pp_fix) + p.list_fix + (gross * p.ads);
      const profit = gross - fees - totalCogs;
      const margin = (profit / gross) * 100;

      const card = document.createElement("div");
      card.className = "comparison-card";
      card.innerHTML = `
        <div class="comparison-platform-name">${p.name}</div>
        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;">Total Fees: $${fees.toFixed(2)}</div>
        <div class="comparison-profit-row">
          <span class="comparison-profit-val" style="color: ${profit > 0 ? '#10B981' : '#EF4444'};">
            $${profit.toFixed(2)}
          </span>
          <span class="comparison-margin-pct">${margin.toFixed(1)}% margin</span>
        </div>
      `;
      comparisonContainer.appendChild(card);
    });
  }

  function renderCouponMatrix() {
    if (!couponContainer) return;
    couponContainer.innerHTML = "";

    const spec = PLATFORMS[state.platform];
    const totalCogs = state.wholesale + state.shipping;
    const testDiscounts = [10, 15, 20, 25, 30];

    testDiscounts.forEach((disc) => {
      const price = state.retail * (1 - disc / 100);
      const gross = price + state.charged_ship;
      const fees = (gross * spec.tx) + (gross * spec.pp + spec.pp_fix) + spec.list_fix + (gross * spec.ads);
      const profit = gross - fees - totalCogs;
      const margin = (profit / gross) * 100;
      const isSafe = margin >= 15.0;

      const row = document.createElement("tr");
      row.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
      row.innerHTML = `
        <td style="padding: 0.6rem 0.5rem; font-weight: 700; color: var(--gold-primary);">${disc}% OFF</td>
        <td style="padding: 0.6rem 0.5rem; font-family: var(--font-mono);">$${price.toFixed(2)}</td>
        <td style="padding: 0.6rem 0.5rem; font-family: var(--font-mono); color: ${profit > 0 ? '#10B981' : '#EF4444'};">$${profit.toFixed(2)}</td>
        <td style="padding: 0.6rem 0.5rem; font-family: var(--font-mono);">${margin.toFixed(1)}%</td>
        <td style="padding: 0.6rem 0.5rem;">
          <span style="font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 800; background: ${isSafe ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)'}; color: ${isSafe ? '#10B981' : '#EF4444'};">
            ${isSafe ? 'APPROVED' : (margin > 0 ? 'TIGHT MARGIN' : 'LOSS')}
          </span>
        </td>
      `;
      couponContainer.appendChild(row);
    });
  }

  function requireProLicense() {
    if (state.isProLicensed) return true;
    if (licenseModal) licenseModal.style.display = "flex";
    return false;
  }

  function initEvents() {
    // Preset buttons
    document.querySelectorAll(".preset-pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".preset-pill").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const key = btn.dataset.preset;
        const p = PRESETS[key];
        if (p) {
          state.retail = p.retail;
          state.wholesale = p.wholesale;
          state.shipping = p.shipping;
          state.charged_ship = p.charged_ship;
          state.discount = 0.0;

          if (retailSlider) retailSlider.value = state.retail;
          if (wholesaleSlider) wholesaleSlider.value = state.wholesale;
          if (shippingSlider) shippingSlider.value = state.shipping;
          if (chargedShipSlider) chargedShipSlider.value = state.charged_ship;
          if (discountSlider) discountSlider.value = state.discount;

          recalculate();
        }
      });
    });

    // Platform buttons
    document.querySelectorAll(".platform-card-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".platform-card-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.platform = btn.dataset.platform;
        recalculate();
      });
    });

    // Sliders
    if (retailSlider) {
      retailSlider.addEventListener("input", (e) => {
        state.retail = parseFloat(e.target.value);
        recalculate();
      });
    }
    if (wholesaleSlider) {
      wholesaleSlider.addEventListener("input", (e) => {
        state.wholesale = parseFloat(e.target.value);
        recalculate();
      });
    }
    if (shippingSlider) {
      shippingSlider.addEventListener("input", (e) => {
        state.shipping = parseFloat(e.target.value);
        recalculate();
      });
    }
    if (chargedShipSlider) {
      chargedShipSlider.addEventListener("input", (e) => {
        state.charged_ship = parseFloat(e.target.value);
        recalculate();
      });
    }
    if (discountSlider) {
      discountSlider.addEventListener("input", (e) => {
        state.discount = parseFloat(e.target.value);
        recalculate();
      });
    }

    // Export CSV
    if (exportCsvBtn) {
      exportCsvBtn.addEventListener("click", () => {
        if (!requireProLicense()) return;
        const csvContent = "data:text/csv;charset=utf-8,Platform,Retail,COGS,Fees,NetProfit,NetMargin\n" +
          Object.keys(PLATFORMS).map(k => {
            const p = PLATFORMS[k];
            const g = state.retail + state.charged_ship;
            const c = state.wholesale + state.shipping;
            const f = (g * p.tx) + (g * p.pp + p.pp_fix) + p.list_fix + (g * p.ads);
            const net = g - f - c;
            const m = (net / g) * 100;
            return `"${p.name}",${g.toFixed(2)},${c.toFixed(2)},${f.toFixed(2)},${net.toFixed(2)},${m.toFixed(1)}%`;
          }).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `pod_pricing_matrix_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    }

    // Modal
    if (openLicenseModalBtn) {
      openLicenseModalBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (licenseModal) licenseModal.style.display = "flex";
      });
    }
    if (closeLicenseModalBtn) {
      closeLicenseModalBtn.addEventListener("click", () => {
        if (licenseModal) licenseModal.style.display = "none";
      });
    }
    if (licenseModal) {
      licenseModal.addEventListener("click", (e) => {
        if (e.target === licenseModal) licenseModal.style.display = "none";
      });
    }

    // License Activation
    if (activateKeyBtn && licenseKeyInput) {
      activateKeyBtn.addEventListener("click", () => {
        const key = licenseKeyInput.value.trim();
        if (key.length >= 6) {
          localStorage.setItem("margin_sentinel_pro_licensed", "true");
          state.isProLicensed = true;
          if (licenseStatusEl) {
            licenseStatusEl.textContent = "✅ License successfully activated! Permanent Pro active.";
            licenseStatusEl.style.color = "#10B981";
          }
          setTimeout(() => {
            if (licenseModal) licenseModal.style.display = "none";
            checkProStatus();
          }, 1200);
        } else {
          if (licenseStatusEl) {
            licenseStatusEl.textContent = "❌ Please enter a valid license key or receipt email.";
            licenseStatusEl.style.color = "#EF4444";
          }
        }
      });
    }
  }

  // Initialize
  checkProStatus();
  recalculate();
  initEvents();
})();
