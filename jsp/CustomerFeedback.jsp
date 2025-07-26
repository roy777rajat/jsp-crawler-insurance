<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Customer Feedback</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
        textarea {width: 400px;}
    </style>
</head>
<body>
    <h2>Customer Feedback Form</h2>
    <form action="SubmitFeedback" method="post">
        <div class="form-field">
            <label for="customerId">Customer ID:</label>
            <input type="text" id="customerId" name="customerId" required />
        </div>
        <div class="form-field">
            <label for="feedback">Feedback:</label><br/>
            <textarea id="feedback" name="feedback" rows="5" required></textarea>
        </div>
        <input type="submit" value="Submit Feedback" />
    </form>
</body>
</html>
