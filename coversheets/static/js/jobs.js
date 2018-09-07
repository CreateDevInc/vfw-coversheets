(function () {
  function getJobNumber() {
    const jobNumber = $('#id_job_number');
    $.get('/admin/coversheets/job_number', function(data) {
      jobNumber.val(data.job_number);
    });
  }

  function initJobNumber() {
    const statuses = ['Done', 'Emergency', 'Production'];
    const jobNumber = $('#id_job_number');

    if (!jobNumber.val()) {
      const statusSelect = $('#id_status');
      statusSelect.change(function (event) {
        const option = statusSelect.find(":selected").text();
        if (statuses.includes(option)) {
          getJobNumber();
        } else {
          jobNumber.val('');
        }
      });
    }
  }

  function initLinks() {
    const albumUrl = $('#id_album_link').val();
    const budgetUrl = $('#id_budget_link').val();
    const scheduleUrl = $('#id_schedule_link').val();

    if (albumUrl) {
      $('.field-album_link .controls')
        .append('<a target="_blank" style="margin-left: 5px;" href="' + $('#id_album_link').val() + '">Go To URL</a>');
    }
    if (budgetUrl) {
      $('.field-budget_link .controls')
        .append('<a target="_blank" style="margin-left: 5px;" href="' + $('#id_budget_link').val() + '">Go To URL</a>');
    }
    if (scheduleUrl) {
      $('.field-schedule_link .controls')
        .append('<a target="_blank" style="margin-left: 5px;" href="' + $('#id_schedule_link').val() + '">Go To URL</a>');
    }

  }

  function getJobId() {
    return window.location.pathname.split('/')[4];
  }

  function initNotes() {
    const hash = window.location.hash;
    if (hash && hash === '#notes') {
      const rowCount = $('.suit-tab-notes .table tr').length;
      if (rowCount < 3) {
        $.get(`/admin/coversheets/job_info/${getJobId()}/`, function (data) {
          const { insurance, lossDesc, program, typeOfLoss } = data;
          $('#id_note_set-0-comment')
            .val(`Program: ${program}\nInsurance Company: ${insurance}\nType of Loss: ${typeOfLoss}\nLoss Information: ${lossDesc}\n`);
        });
      }
    }
  }

  $(document).ready(function() {
    const path = window.location.pathname;
    const hash = window.location.hash;

    window.addEventListener('hashchange', initNotes);

    if (hash && hash === '#notes') {
      initNotes();
    }

    if (
      path === '/admin/coversheets/job/add/' ||
      /\/admin\/coversheets\/job\/\d+/.test(path)
    ) {
      initJobNumber();
      initLinks();
      setTimeout(() => {
        $('.field-loss_year_built .datetimeshortcuts').hide();
      }, 200);
    }
  });
})();
