function start_download(resource_id) {
    const $spinner = $("#download-spinner");
    $spinner.css("display", "inline-block");

    $.ajax({
        url: "/databricks/download/start",
        method: "POST",
        data: JSON.stringify({ resource_id: resource_id }),
        contentType: "application/json",
        success: function (response) {
            const taskId = response.task_id;
            const downloadUrl = response.download_url;
            pollDownloadTaskStatus(taskId, downloadUrl, $spinner);
        },
        error: function () {
            $spinner.hide()
            window.location.reload();
        }
    });
};

function pollDownloadTaskStatus(taskId, downloadUrl, $spinner) {
    $.ajax({
        url: "/databricks/download/status",
        method: "POST",
        data: JSON.stringify({ task_id: taskId }),
        contentType: "application/json",
        success: function (response) {
            const status = response.status;
            if (status === "completed") {
                $spinner.hide()
                window.location.href = downloadUrl;
            } else if (status === "error") {
                $spinner.hide()
                window.location.reload();
            } else {
                setTimeout(() => pollDownloadTaskStatus(taskId, downloadUrl), 2000);
            }
        },
        error: function () {
            $spinner.hide()
            window.location.reload();
        }
    });
}

function start_query_download(resource_id, query_id, format) {
    const $spinner = $("#query-spinner-" + query_id);
    $spinner.css("display", "inline-block");

    $.ajax({
        url: "/databricks/query/start_download",
        method: "POST",
        data: JSON.stringify({ 
            resource_id: resource_id, 
            query_id: query_id,
            format: format
        }),
        contentType: "application/json",
        success: function (response) {
            const taskId = response.task_id;
            const downloadUrl = response.download_url;
            pollQueryDownloadTaskStatus(taskId, downloadUrl, $spinner);
        },
        error: function () {
            $spinner.hide()
            window.location.reload();
        }
    });
}

function pollQueryDownloadTaskStatus(taskId, downloadUrl, $spinner) {
    $.ajax({
        url: "/databricks/query/status",
        method: "POST",
        data: JSON.stringify({ task_id: taskId }),
        contentType: "application/json",
        success: function (response) {
            const status = response.status;
            if (status === "completed") {
                $spinner.hide()
                window.location.href = downloadUrl;
            } else if (status === "error") {
                $spinner.hide()
                window.location.reload();
                document.getElementById('tdh-query-response-0').innerHTML = response.message
            } else {
                setTimeout(() => pollQueryDownloadTaskStatus(taskId, downloadUrl, $spinner), 2000);
            }
        },
        error: function () {
            $spinner.hide()
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
