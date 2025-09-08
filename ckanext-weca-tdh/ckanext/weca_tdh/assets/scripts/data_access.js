function start_download(resource_id) {
    $("#spinner").css("display", "inline-block");

    $.ajax({
        url: "/databricks/download/start",
        method: "POST",
        data: JSON.stringify({ resource_id: resource_id }),
        contentType: "application/json",
        success: function (response) {
        const taskId = response.task_id;
        const downloadUrl = response.download_url;
        pollTaskStatus(taskId, downloadUrl);
        },
        error: function (err) {
        $("#spinner").css("display", "none");
        window.location.reload();
        }
    });
};

function pollTaskStatus(taskId, downloadUrl) {
    $.ajax({
        url: "/databricks/download/status",
        method: "POST",
        data: JSON.stringify({ task_id: taskId }),
        contentType: "application/json",
        success: function (response) {
        const status = response.status;
        if (status === "completed") {
            $("#spinner").css("display", "none");
            window.location.href = downloadUrl;
        } else if (status === "error") {
            $("#spinner").css("display", "none");
            window.location.reload();
        } else {
            setTimeout(() => pollTaskStatus(taskId, downloadUrl), 2000);
        }
        },
        error: function (err) {
        $("#spinner").css("display", "none");
        window.location.reload();
        }
    });
}

function copyQueryPath() {
  const text = document.getElementById('tdh-query-path').innerText;
  const icon = document.getElementById('tdh-query-path-icon');

  navigator.clipboard.writeText(text).then(() => {
    icon.classList.remove('fa-regular');
    icon.classList.add('fa-solid');

    setTimeout(() => {
      icon.classList.remove('fa-solid');
      icon.classList.add('fa-regular');
    }, 500);
  });
}
