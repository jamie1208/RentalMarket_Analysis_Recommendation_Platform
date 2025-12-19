const houseImages = [
  "/static/images/houses/house_01.png",
  "/static/images/houses/house_02.png",
  "/static/images/houses/house_03.png",
  "/static/images/houses/house_04.png",
  "/static/images/houses/house_05.png",
  "/static/images/houses/house_06.png",
  "/static/images/houses/house_07.png",
  "/static/images/houses/house_08.png",
  "/static/images/houses/house_09.png",
  "/static/images/houses/house_10.png",
];
const cluster = localStorage.getItem("cluster");
let currentPage = 1;

// ===== DOM =====
const grid = document.getElementById("card-grid");
const pagination = document.getElementById("pagination");
document.getElementById("applyFilter").onclick = () => {
  loadData(1); // 套用篩選後回到第一頁
};

// ===== 抓資料 =====
function loadData(page = 1) {
  currentPage = page;

  const query = getFilters();

  fetch(`/api/rent/by-cluster?${query}`)
    .then((res) => res.json())
    .then((data) => {
      renderCards(data.houses);
      renderPagination(data.total_pages, data.page);
    })
    .catch((err) => console.error(err));
}

// ===== 畫房屋卡片 =====
function renderCards(houses) {
  grid.innerHTML = "";

  houses.forEach((h) => {
    const link = document.createElement("a");
    link.href = `/house/${h.id}`;
    link.className = "house-card";
    link.style.textDecoration = "none";
    link.style.color = "inherit";

    const randomImg =
      houseImages[Math.floor(Math.random() * houseImages.length)];

    link.innerHTML = `
        <div class="image" style="background-image: url('${randomImg}')"></div>
      <h3>${h.district}</h3>
      <p>${h.area_ping} 坪 · $${h.total_rent.toLocaleString()} / 月</p>
    `;

    grid.appendChild(link);
  });
}

// ===== 畫分頁 =====
function renderPagination(totalPages, current) {
  const container = document.getElementById("pagination");
  container.innerHTML = "";

  const maxVisible = 5; // 最多顯示幾個頁碼
  let start = Math.max(1, current - 2);
  let end = Math.min(totalPages, current + 2);

  // 修正頭尾不足的情況
  if (current <= 3) {
    start = 1;
    end = Math.min(totalPages, maxVisible);
  }

  if (current >= totalPages - 2) {
    end = totalPages;
    start = Math.max(1, totalPages - maxVisible + 1);
  }

  // « 上一頁
  if (current > 1) {
    const prev = document.createElement("span");
    prev.textContent = "«";
    prev.onclick = () => loadData(current - 1);
    container.appendChild(prev);
  }

  // 頁碼
  for (let i = start; i <= end; i++) {
    const btn = document.createElement("span");
    btn.textContent = i;
    if (i === current) btn.classList.add("active");

    btn.onclick = () => loadData(i);
    container.appendChild(btn);
  }

  // » 下一頁
  if (current < totalPages) {
    const next = document.createElement("span");
    next.textContent = "»";
    next.onclick = () => loadData(current + 1);
    container.appendChild(next);
  }
}
// 篩選條件
function getFilters() {
  const rent = document.getElementById("rent").value;
  const district = document.getElementById("district").value;

  let params = new URLSearchParams();

  if (rent) {
    const [min, max] = rent.split("-");
    params.append("rent_min", min);
    params.append("rent_max", max);
  }

  if (district) {
    params.append("district", district);
  }

  params.append("cluster", cluster);
  params.append("p", currentPage);

  return params.toString();
}
//找行政區
function loadDistricts() {
  fetch("/api/districts")
    .then((res) => res.json())
    .then((districts) => {
      const select = document.getElementById("district");

      districts.forEach((d) => {
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = d;
        select.appendChild(opt);
      });
    })
    .catch((err) => console.error("載入行政區失敗", err));
}

// ===== 初始化 =====
// ===== 初始化 =====
loadDistricts();

loadData(currentPage);
