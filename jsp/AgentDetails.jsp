<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Agent Details</title>
    <style>
        label {width: 150px; font-weight: bold;}
        .form-field {margin-bottom: 10px;}
    </style>
</head>
<body>
    <h2>Insurance Agent Details</h2>
    <form action="UpdateAgent" method="post">
        <div class="form-field">
            <label for="agentId">Agent ID:</label>
            <input type="text" id="agentId" name="agentId" value="${agent.agentId}" readonly />
        </div>
        <div class="form-field">
            <label for="agentName">Agent Name:</label>
            <input type="text" id="agentName" name="agentName" value="${agent.agentName}" required />
        </div>
        <div class="form-field">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" value="${agent.email}" required />
        </div>
        <div class="form-field">
            <label for="phone">Phone Number:</label>
            <input type="tel" id="phone" name="phone" value="${agent.phone}" required />
        </div>
        <div class="form-field">
            <label for="region">Region:</label>
            <input type="text" id="region" name="region" value="${agent.region}" />
        </div>
        <input type="submit" value="Update Agent" />
    </form>
</body>
</html>
