<%@ page language="java" contentType="text/html;charset=UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<html>
<head><title>claimStatus.jsp</title></head>
<body>
<h2>Check claim status</h2>

<form action="/claimStatus" method="post">
    <label for="policyNumber">Policy Number:</label>
    <input type="text" id="policyNumber" name="policyNumber" value="${policy.policyNumber}" /><br/>

    <label for="sumAssured">Sum Assured:</label>
    <input type="number" id="sumAssured" name="sumAssured" value="${policy.sumAssured}" /><br/>

    <label for="dob">Date of Birth:</label>
    <input type="date" id="dob" name="dob" value="${customer.dob}" /><br/>

    <label for="gender">Gender:</label>
    <select id="gender" name="gender">
        <option value="M" ${gender == 'M' ? 'selected' : ''}>Male</option>
        <option value="F" ${gender == 'F' ? 'selected' : ''}>Female</option>
        <option value="O" ${gender == 'O' ? 'selected' : ''}>Other</option>
    </select><br/>

    <label for="claimReason">Claim Reason:</label>
    <textarea id="claimReason" name="claimReason" rows="4" cols="50">${claim.reason}</textarea><br/>

    <label for="agentId">Agent:</label>
    <input type="text" id="agentId" name="agentId" value="${agent.id}" />
    <button type="button" onclick="lookupAgent()">Lookup</button><br/>

    <input type="submit" value="Submit" />
    <input type="reset" value="Reset" />
    <button type="button" onclick="goBack()">Back</button>
</form>

<script>
function lookupAgent() {
    alert("Agent lookup not implemented yet.");
}
function goBack() {
    window.history.back();
}
</script>
</body>
</html>
