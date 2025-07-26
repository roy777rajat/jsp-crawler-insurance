<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Policy Cancellation</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Policy Cancellation Request</h2>
    <form action="CancelPolicy" method="post">
        <div class="form-field">
            <label for="policyNumber">Policy Number:</label>
            <input type="text" id="policyNumber" name="policyNumber" required />
        </div>
        <div class="form-field">
            <label for="cancellationDate">Cancellation Date:</label>
            <input type="date" id="cancellationDate" name="cancellationDate" value="<%= new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date()) %>" required />
        </div>
        <div class="form-field">
            <label for="reason">Reason for Cancellation:</label><br/>
            <textarea id="reason" name="reason" rows="3" cols="40" required></textarea>
        </div>
        <input type="submit" value="Submit Cancellation" />
    </form>
</body>
</html>
