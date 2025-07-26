%@ page language=java contentType=texthtml; charset=UTF-8 pageEncoding=UTF-8%
html
head
    titleNew Insurance Quotationtitle
    style
        label {display inline-block; width 180px; font-weight bold;}
        .form-field {margin-bottom 12px;}
    style
    script
        function validateForm() {
            var amount = document.forms[quoteForm][sumAssured].value;
            if (isNaN(amount)  amount = 0) {
                alert(Please enter a valid Sum Assured amount.);
                return false;
            }
            return true;
        }
    script
head
body
    h2Create New Quotationh2
    form name=quoteForm action=SubmitQuotation method=post onsubmit=return validateForm()
        div class=form-field
            label for=customerIdCustomer IDlabel
            input type=text id=customerId name=customerId required 
        div
        div class=form-field
            label for=productTypeProduct Typelabel
            select id=productType name=productType required
                option value=-- Select --option
                option value=TermLifeTerm Life Insuranceoption
                option value=HealthHealth Insuranceoption
                option value=EndowmentEndowment Planoption
                option value=ULIPULIPoption
            select
        div
        div class=form-field
            label for=sumAssuredSum Assured (₹)label
            input type=number id=sumAssured name=sumAssured min=100000 required 
        div
        div class=form-field
            label for=premiumModePremium Modelabel
            select id=premiumMode name=premiumMode required
                option value=-- Select --option
                option value=MonthlyMonthlyoption
                option value=QuarterlyQuarterlyoption
                option value=HalfYearlyHalf-Yearlyoption
                option value=YearlyYearlyoption
            select
        div
        div class=form-field
            label for=policyTermPolicy Term (years)label
            input type=number id=policyTerm name=policyTerm min=1 max=50 required 
        div
        div class=form-field
            label for=remarksRemarkslabelbr
            textarea id=remarks name=remarks rows=3 cols=40textarea
        div
        input type=submit value=Generate Quotation 
    form
body
html
