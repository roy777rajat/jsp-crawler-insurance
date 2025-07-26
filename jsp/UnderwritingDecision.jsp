<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Underwriting Decision</title>
    <style>
        label {width: 180px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
        textarea {width: 400px;}
    </style>
</head>
<body>
    <h2>Underwriting Decision</h2>
    <form action="SubmitUnderwriting" method="post">
        <div class="form-field">
            <label for="applicationId">Application ID:</label>
            <input type="text" id="applicationId" name="applicationId" value="${application.applicationId}" readonly />
        </div>
        <div class="form-field">
            <label for="decision">Decision:</label>
            <select id="decision" name="decision" required>
                <option value="">--Select--</option>
                <option value="Approved" ${application.decision == 'Approved' ? 'selected' : ''}>Approved</option>
                <option value="Rejected" ${application.decision == 'Rejected' ? 'selected' : ''}>Rejected</option>
                <option value="Pending" ${application.decision == 'Pending' ? 'selected' : ''}>Pending</option>
            </select>
        </div>
        <div class="form-field">
            <label for="comments">Comments:</label><br/>
            <textarea id="comments" name="comments" rows="4">${application.comments}</textarea>
        </div>
        <input type="submit" value="Submit Decision" />
    </form>
</body>
</html>
