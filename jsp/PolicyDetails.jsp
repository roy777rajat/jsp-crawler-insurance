<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Policy Details</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Policy Details</h2>
    <form action="UpdatePolicy" method="post">
        <div class="form-field">
            <label for="policyNumber">Policy Number:</label>
            <input type="text" id="policyNumber" name="policyNumber" value="${policy.policyNumber}" readonly />
        </div>
        <div class="form-field">
            <label for="customerId">Customer ID:</label>
            <input type="text" id="customerId" name="customerId" value="${policy.customerId}" readonly />
        </div>
        <div class="form-field">
            <label for="productType">Product Type:</label>
            <input type="text" id="productType" name="productType" value="${policy.productType}" readonly />
        </div>
        <div class="form-field">
            <label for="sumAssured">Sum Assured:</label>
            <input type="number" id="sumAssured" name="sumAssured" value="${policy.sumAssured}" required />
        </div>
        <div class="form-field">
            <label for="premiumAmount">Premium Amount:</label>
            <input type="number" id="premiumAmount" name="premiumAmount" value="${policy.premiumAmount}" required />
        </div>
        <div class="form-field">
            <label for="policyStartDate">Policy Start Date:</label>
            <input type="date" id="policyStartDate" name="policyStartDate" value="${policy.policyStartDate}" required />
        </div>
        <div class="form-field">
            <label for="policyEndDate">Policy End Date:</label>
            <input type="date" id="policyEndDate" name="policyEndDate" value="${policy.policyEndDate}" required />
        </div>
        <div class="form-field">
            <label for="status">Status:</label>
            <select id="status" name="status" required>
                <option value="Active" ${policy.status == 'Active' ? 'selected' : ''}>Active</option>
                <option value="Lapsed" ${policy.status == 'Lapsed' ? 'selected' : ''}>Lapsed</option>
                <option value="Cancelled" ${policy.status == 'Cancelled' ? 'selected' : ''}>Cancelled</option>
            </select>
        </div>
        <input type="submit" value="Update Policy" />
    </form>
</body>
</html>
