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

  function initNotes() {
    const hash = window.location.hash;
    if (hash && hash === '#notes') {
      const rowCount = $('.suit-tab-notes .table tr').length;
      if (rowCount < 3) {
        $('#id_note_set-0-comment').val('Program:\nInsurance Company:\nType of Loss:\nLoss Description:');
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
    }
  });
})();
