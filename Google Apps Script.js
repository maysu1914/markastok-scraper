sortByAvailability();
sendEmails();

function sortByAvailability(callback) {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getRange("A2:G"); 
  range.sort(4); // availability column
  SpreadsheetApp.flush();
}

function sendEmails() {
  var ss_id = SpreadsheetApp.getActiveSpreadsheet().getId();
  var file = DriveApp.getFileById(ss_id);
  MailApp.sendEmail('example@example.com', 'Mustafa Aysu - Software Developer Case Study', 'Please see the attached file.', {
    attachments: [file.getBlob()],
    name: 'Mustafa Aysu'
  });
}