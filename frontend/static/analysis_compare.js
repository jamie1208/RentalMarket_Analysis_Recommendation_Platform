fetch("/api/cluster/summary")
  .then((res) => res.json())
  .then((data) => {
    const labels = ["新婚族", "家庭租屋族", "豪宅族", "學生 / 單身上班族"];

    const avgRent = data.map((d) => d.avg_rent);
    const avgSize = data.map((d) => d.avg_size);
    const avgAge = data.map((d) => d.avg_age);

    const colors = ["#7BA7BC", "#8FC1A9", "#E6B566", "#D98C8C"];

    // ===== 平均租金 =====
    new Chart(document.getElementById("rentChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "平均租金（元）",
            data: avgRent,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // ⭐ 一定要
        plugins: {
          title: {
            display: true,
            text: "平均租金比較",
          },
        },
      },
    });

    // ===== 平均坪數 =====
    new Chart(document.getElementById("areaChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "平均坪數",
            data: avgSize,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // ⭐ 一定要
        plugins: {
          title: {
            display: true,
            text: "平均坪數比較",
          },
        },
      },
    });

    // ===== 平均屋齡 =====
    new Chart(document.getElementById("ageChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "平均屋齡（年）",
            data: avgAge,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // ⭐ 一定要
        plugins: {
          title: {
            display: true,
            text: "平均屋齡比較",
          },
        },
      },
    });
  });
