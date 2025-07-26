<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html>
<head>
    <title>Agent Commission Report</title>
    <style>
        table {
            width: 80%;
            border-collapse: collapse;
            margin: auto;
        }
        th, td {
            padding: 8px 12px;
            border: 1px solid #ddd;
            text-align: center;
        }
        th {
            background-color: #f4f4f4;
        }
    </style>
</head>
<body>
    <h2>Agent Commission Report</h2>
    <form action="GenerateCommissionReport" method="get" style="text-align:center; margin-bottom:20px;">
        <label for="agentId">Agent ID:</label>
        <input type="text" id="agentId" name="agentId" required />
        <label for="fromDate">From:</label>
        <input type="date" id="fromDate" name="fromDate" required />
        <label for="toDate">To:</label>
        <input type="date" id="toDate" name="toDate" required />
        <input type="submit" value="Generate" />
    </form>
    <c:if test="${not empty report}">
        <table>
            <tr>
                <th>Policy Number</th>
                <th>Commission Amount</th>
                <th>Payment Date</th>
            </tr>
            <c:forEach var="item" items="${report}">
                <tr>
                    <td>${item.policyNumber}</td>
                    <td>₹${item.commissionAmount}</td>
                    <td>${item.paymentDate}</td>
                </tr>
            </c:forEach>
        </table>
    </c:if>
</body>
</html>
