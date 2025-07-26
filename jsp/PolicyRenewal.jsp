<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Policy Renewal</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Policy Renewal</h2>
    <form action="RenewPolicy" method="post">
        <div class="form-field">
            <label for="policyNumber">Policy Number:</label>
            <input type="text" id="policyNumber" name="policyNumber" required />
        </div>
        <div class="form-field">
            <label for="renewalDate">Renewal Date:</label>
            <input type="date" id="renewalDate" name="renewalDate" value="<%= new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date()) %>" required />
        </div>
        <div class="form-field">
            <label for="premiumAmount">Premium Amount (₹):</label>
            <input type="number" id="premiumAmount" name="premiumAmount" min="1" required />
        </div>
        <input type="submit" value="Renew Policy" />
    </form>
</body>
</html>
