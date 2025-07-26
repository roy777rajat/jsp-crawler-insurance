<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Premium Payment</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Premium Payment</h2>
    <form action="ProcessPayment" method="post">
        <div class="form-field">
            <label for="paymentId">Payment ID:</label>
            <input type="text" id="paymentId" name="paymentId" readonly value="${payment.paymentId}" />
        </div>
        <div class="form-field">
            <label for="policyNumber">Policy Number:</label>
            <input type="text" id="policyNumber" name="policyNumber" required />
        </div>
        <div class="form-field">
            <label for="amount">Amount (?):</label>
            <input type="number" id="amount" name="amount" min="1" required />
        </div>
        <div class="form-field">
            <label for="paymentDate">Payment Date:</label>
            <input type="date" id="paymentDate" name="paymentDate" value="<%= new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date()) %>" required />
        </div>
        <div class="form-field">
            <label for="paymentMode">Payment Mode:</label>
            <select id="paymentMode" name="paymentMode" required>
                <option value="">--Select--</option>
                <option value="Cash">Cash</option>
                <option value="Cheque">Cheque</option>
                <option value="Online">Online Transfer</option>
                <option value="NEFT">NEFT/RTGS</option>
            </select>
        </div>
        <input type="submit" value="Submit Payment" />
    </form>
</body>
</html>
