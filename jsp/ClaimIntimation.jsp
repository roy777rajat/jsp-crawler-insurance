<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Claim Intimation</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Claim Intimation Form</h2>
    <form action="SubmitClaimIntimation" method="post">
        <div class="form-field">
            <label for="claimId">Claim ID:</label>
            <input type="text" id="claimId" name="claimId" readonly value="${claim.claimId}" />
        </div>
        <div class="form-field">
            <label for="policyNumber">Policy Number:</label>
            <input type="text" id="policyNumber" name="policyNumber" required />
        </div>
        <div class="form-field">
            <label for="dateOfLoss">Date of Loss:</label>
            <input type="date" id="dateOfLoss" name="dateOfLoss" required />
        </div>
        <div class="form-field">
            <label for="claimType">Claim Type:</label>
            <select id="claimType" name="claimType" required>
                <option value="">--Select--</option>
                <option value="Death">Death</option>
                <option value="Accident">Accident</option>
                <option value="Hospitalization">Hospitalization</option>
                <option value="Maturity">Maturity</option>
            </select>
        </div>
        <div class="form-field">
            <label for="claimAmount">Claim Amount (?):</label>
            <input type="number" id="claimAmount" name="claimAmount" min="0" required />
        </div>
        <div class="form-field">
            <label for="intimationDate">Intimation Date:</label>
            <input type="date" id="intimationDate" name="intimationDate" value="<%= new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date()) %>" required />
        </div>
        <div class="form-field">
            <label for="remarks">Remarks:</label><br/>
            <textarea id="remarks" name="remarks" rows="3" cols="40"></textarea>
        </div>
        <input type="submit" value="Submit Intimation" />
    </form>
</body>
</html>
