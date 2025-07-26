<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Claim Status</title>
    <style>
        table {
            border-collapse: collapse;
            width: 80%;
            margin: auto;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px 12px;
            text-align: center;
        }
        th {
            background-color: #eee;
        }
    </style>
</head>
<body>
    <h2>Claim Status</h2>
    <form action="SearchClaim" method="get" style="text-align:center; margin-bottom:20px;">
        <input type="text" name="claimId" placeholder="Enter Claim ID" required />
        <input type="submit" value="Search" />
    </form>
    
    <c:if test="${not empty claim}">
        <table>
            <tr>
                <th>Claim ID</th>
                <th>Policy Number</th>
                <th>Status</th>
                <th>Claim Amount</th>
                <th>Settlement Date</th>
            </tr>
            <tr>
                <td>${claim.claimId}</td>
                <td>${claim.policyNumber}</td>
                <td>${claim.status}</td>
                <td>₹${claim.claimAmount}</td>
                <td>${claim.settlementDate}</td>
            </tr>
        </table>
    </c:if>
</body>
</html>
