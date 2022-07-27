let country_list = {
    "AED" : "AE",
    "AFN" : "AF",
    "XCD" : "AG",
    "ALL" : "AL",
    "AMD" : "AM",
    "ANG" : "AN",
    "AOA" : "AO",
    "AQD" : "AQ",
    "ARS" : "AR",
    "AUD" : "AU",
    "AZN" : "AZ",
    "BAM" : "BA",
    "BBD" : "BB",
    "BDT" : "BD",
    "XOF" : "BE",
    "BGN" : "BG",
    "BHD" : "BH",
    "BIF" : "BI",
    "BMD" : "BM",
    "BND" : "BN",
    "BOB" : "BO",
    "BRL" : "BR",
    "BSD" : "BS",
    "NOK" : "BV",
    "BWP" : "BW",
    "BYR" : "BY",
    "BZD" : "BZ",
    "CAD" : "CA",
    "CDF" : "CD",
    "XAF" : "CF",
    "CHF" : "CH",
    "CLP" : "CL",
    "CNY" : "CN",
    "COP" : "CO",
    "CRC" : "CR",
    "CUP" : "CU",
    "CVE" : "CV",
    "CYP" : "CY",
    "CZK" : "CZ",
    "DJF" : "DJ",
    "DKK" : "DK",
    "DOP" : "DO",
    "DZD" : "DZ",
    "ECS" : "EC",
    "EEK" : "EE",
    "EGP" : "EG",
    "ETB" : "ET",
    "EUR" : "FR",
    "FJD" : "FJ",
    "FKP" : "FK",
    "GBP" : "GB",
    "GEL" : "GE",
    "GGP" : "GG",
    "GHS" : "GH",
    "GIP" : "GI",
    "GMD" : "GM",
    "GNF" : "GN",
    "GTQ" : "GT",
    "GYD" : "GY",
    "HKD" : "HK",
    "HNL" : "HN",
    "HRK" : "HR",
    "HTG" : "HT",
    "HUF" : "HU",
    "IDR" : "ID",
    "ILS" : "IL",
    "INR" : "IN",
    "IQD" : "IQ",
    "IRR" : "IR",
    "ISK" : "IS",
    "JMD" : "JM",
    "JOD" : "JO",
    "JPY" : "JP",
    "KES" : "KE",
    "KGS" : "KG",
    "KHR" : "KH",
    "KMF" : "KM",
    "KPW" : "KP",
    "KRW" : "KR",
    "KWD" : "KW",
    "KYD" : "KY",
    "KZT" : "KZ",
    "LAK" : "LA",
    "LBP" : "LB",
    "LKR" : "LK",
    "LRD" : "LR",
    "LSL" : "LS",
    "LTL" : "LT",
    "LVL" : "LV",
    "LYD" : "LY",
    "MAD" : "MA",
    "MDL" : "MD",
    "MGA" : "MG",
    "MKD" : "MK",
    "MMK" : "MM",
    "MNT" : "MN",
    "MOP" : "MO",
    "MRO" : "MR",
    "MTL" : "MT",
    "MUR" : "MU",
    "MVR" : "MV",
    "MWK" : "MW",
    "MXN" : "MX",
    "MYR" : "MY",
    "MZN" : "MZ",
    "NAD" : "NA",
    "XPF" : "NC",
    "NGN" : "NG",
    "NIO" : "NI",
    "NPR" : "NP",
    "NZD" : "NZ",
    "OMR" : "OM",
    "PAB" : "PA",
    "PEN" : "PE",
    "PGK" : "PG",
    "PHP" : "PH",
    "PKR" : "PK",
    "PLN" : "PL",
    "PYG" : "PY",
    "QAR" : "QA",
    "RON" : "RO",
    "RSD" : "RS",
    "RUB" : "RU",
    "RWF" : "RW",
    "SAR" : "SA",
    "SBD" : "SB",
    "SCR" : "SC",
    "SDG" : "SD",
    "SEK" : "SE",
    "SGD" : "SG",
    "SKK" : "SK",
    "SLL" : "SL",
    "SOS" : "SO",
    "SRD" : "SR",
    "STD" : "ST",
    "SVC" : "SV",
    "SYP" : "SY",
    "SZL" : "SZ",
    "THB" : "TH",
    "TJS" : "TJ",
    "TMT" : "TM",
    "TND" : "TN",
    "TOP" : "TO",
    "TRY" : "TR",
    "TTD" : "TT",
    "TWD" : "TW",
    "TZS" : "TZ",
    "UAH" : "UA",
    "UGX" : "UG",
    "USD" : "US",
    "UYU" : "UY",
    "UZS" : "UZ",
    "VEF" : "VE",
    "VND" : "VN",
    "VUV" : "VU",
    "YER" : "YE",
    "ZAR" : "ZA",
    "ZMK" : "ZM",
    "ZWD" : "ZW"
}

const droplist = document.querySelectorAll(".drop-list select");
const primaryCurrency = document.getElementById("primary");
const secondaryCurrency = document.getElementById("secondary");
primaryCurrency.innerHTML = country_list;
secondaryCurrency.innerHTML = country_list;


function getOptions(data) {
  return Object.entries(data)
    .map(([country, currency]) => `<option value="${country}">${country}</option>`)
    .join("");
}

document.getElementById("btn-convert").addEventListener("click", fetchCurrencies);

function fetchCurrencies() {
  const primary = primaryCurrency.value;
  const secondary = secondaryCurrency.value;
  const amount = document.getElementById("amount").value;
  const fc = document.getElementById("Claim_Amount_FC").value;
  // Important: Include your API key below
  fetch("https://v6.exchangerate-api.com/v6/10e6be3a3cbd346c984a5c01/latest/" + primary)
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("NETWORK RESPONSE ERROR");
      }
    })
    .then((data) => {
      console.log(data);
      displayCurrency(data, primary, secondary, amount);
    })
    .catch(() => {
      exchangeRateTxt.innerText = "Something went wrong";
    });
}

function displayCurrency(data, primary, secondary, amount) {
  const calculated = amount * data.conversion_rates[secondary];
  const forex = data.conversion_rates[secondary]
  const ori = amount
  document.getElementById("txt-primary").innerText = amount + " " + primary + " = ";
  document.getElementById("conversion_rate").value = forex;
  document.getElementById("txt-secondary").innerText = calculated + " " + secondary;
  document.getElementById("Claim_Amount_SGD").value = calculated;
  document.getElementById("Claim_Amount_FC").value = amount;
}

for (let i = 0; i < droplist.length; i++) {
  for (let country_list in country_list) {
    let selected;
    if (i == 0) {
      selected = country_list == "USD" ? "selected" : "";
    } else if (i == 1) {
      selected = country_list == "SGD" ? "selected" : "";
    }
    let optionTag = `<option value="${country_list}" ${selected}>${country_list}</option>`;
    droplist[i].insertAdjacentHTML("beforeend", optionTag)
  }
  droplist[i].addEventListener("change", e => {
    loadFlag(e.target)
  });

}

window.addEventListener("load", () => {
  getExchangeRate();
})


getButton.addEventListener("click", e => {
  e.preventDefault()
  getExchangeRate();
})


function loadFlag(e) {
for (code in country_list) {
  if (code == e.value) {
    const country = country_list[code].toLowerCase();
    let imgTag = e.parentElement.querySelector('img')
    imgTag.src = `https://flagcdn.com/48x36/${country}.png`;
    imgTag.srcset = `https://flagcdn.com/96x72/${country}.png 2x, https://flagcdn.com/144x108/${country}.png 3x`;
    imgTag.alt = country;
  }
}
}

const exchangeIcon = document.querySelector("form .icon");
exchangeIcon.addEventListener("click", () => {
  let tempCode = primaryCurrency.value;
  primaryCurrency.value = secondaryCurrency.value;
  secondaryCurrency.value = tempCode;
  loadFlag(primaryCurrency);
  loadFlag(secondaryCurrency);
  getExchangeRate();
})




