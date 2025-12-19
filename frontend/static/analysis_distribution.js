fetch("/api/cluster_distribution")
  .then((res) => res.json())
  .then((result) => {
    const ctx = document.getElementById("clusterChart").getContext("2d");

    const total = result.data.reduce((a, b) => a + b, 0);

    new Chart(ctx, {
      type: "pie",
      data: {
        labels: ["新婚族", "家庭租屋族", "豪宅族", "學生 / 單身上班族"],
        datasets: [
          {
            data: result.data,
            backgroundColor: ["#7BA7BC", "#8FC1A9", "#E6B566", "#D98C8C"],
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: 30 },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 14,
              padding: 20,
              font: {
                size: 14,
                family: "Noto Sans TC",
              },
            },
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const value = ctx.parsed;
                const percent = ((value / total) * 100).toFixed(1);
                return `${ctx.label}：${value} 筆（${percent}%）`;
              },
            },
          },
          title: {
            display: true,
            text: "租屋市場族群分布",
            font: { size: 20, weight: "bold" },
            padding: { bottom: 20 },
          },
        },
      },
    });
  });
