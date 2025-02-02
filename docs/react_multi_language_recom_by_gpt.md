Building a **multi-language React frontend** requires proper **internationalization (i18n)** support. The **recommended** way is to use **react-i18next**, as it provides powerful translation capabilities, including dynamic content, interpolation, and formatting.

---

## **Recommended Approach: Using `react-i18next`**
### **1. Install Dependencies**
Run the following command:
```sh
npm install i18next react-i18next i18next-browser-languagedetector i18next-http-backend
```

- **`i18next`** – Core internationalization library.
- **`react-i18next`** – React bindings for `i18next`.
- **`i18next-browser-languagedetector`** – Detects browser language automatically.
- **`i18next-http-backend`** – Loads translations from an external file.

---

### **2. Set Up Translation Configuration (`i18n.js`)**
Create a new file **`src/i18n.js`** to configure the translation settings.

```javascript
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import HttpBackend from "i18next-http-backend";

i18n
  .use(HttpBackend) // Load translations from JSON files
  .use(LanguageDetector) // Detect browser language
  .use(initReactI18next) // Initialize react-i18next
  .init({
    fallbackLng: "en", // Default language
    debug: true,
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ["querystring", "localStorage", "cookie", "navigator"], // Detect language
      caches: ["localStorage", "cookie"], // Save language choice
    },
  });

export default i18n;
```

---

### **3. Create Translation Files**
Create a **`locales/`** folder in **`public/`**:
```
public/locales/
 ├── en/translation.json
 ├── jp/translation.json
 ├── ru/translation.json
```
Each file will contain translations.

#### **English (`public/locales/en/translation.json`)**
```json
{
  "welcome": "Welcome to our shop",
  "add_to_cart": "Add to Cart",
  "checkout": "Proceed to Checkout"
}
```

#### **Japanese (`public/locales/jp/translation.json`)**
```json
{
  "welcome": "私たちのショップへようこそ",
  "add_to_cart": "カートに追加",
  "checkout": "チェックアウトへ進む"
}
```

#### **Russian (`public/locales/ru/translation.json`)**
```json
{
  "welcome": "Добро пожаловать в наш магазин",
  "add_to_cart": "Добавить в корзину",
  "checkout": "Перейти к оплате"
}
```

---

### **4. Load Translations in `App.js`**
Modify your **`src/App.js`** to use translations.

```javascript
import React from "react";
import { useTranslation } from "react-i18next";
import "./i18n"; // Import i18n configuration

function App() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="App">
      <h1>{t("welcome")}</h1>
      <button onClick={() => changeLanguage("en")}>English</button>
      <button onClick={() => changeLanguage("jp")}>日本語</button>
      <button onClick={() => changeLanguage("ru")}>Русский</button>
      <button>{t("add_to_cart")}</button>
      <button>{t("checkout")}</button>
    </div>
  );
}

export default App;
```

---

### **5. Persist User’s Language Preference**
Modify **`i18n.js`** to save the language selection:
```javascript
detection: {
  order: ["localStorage", "cookie", "querystring", "navigator"],
  caches: ["localStorage", "cookie"], // Save the language
}
```
Now, when a user changes the language, their choice will be remembered in **localStorage** or **cookies**.

---

### **6. Format Dates and Numbers (Optional)**
If your eCommerce app needs **date and number formatting**, use `react-intl`.

```sh
npm install react-intl
```
Example:
```javascript
import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";

function Price({ value }) {
  const { i18n } = useTranslation();
  const [price, setPrice] = useState("");

  useEffect(() => {
    setPrice(
      new Intl.NumberFormat(i18n.language, { style: "currency", currency: "USD" }).format(value)
    );
  }, [i18n.language, value]);

  return <span>{price}</span>;
}
```

---

### **7. Dynamic Translations for Backend Data**
If your backend sends **product data in different languages**, handle translations dynamically:
```javascript
const ProductDetails = ({ product }) => {
  const { i18n } = useTranslation();
  
  return (
    <div>
      <h2>{product.name[i18n.language] || product.name["en"]}</h2>
      <p>{product.description[i18n.language] || product.description["en"]}</p>
    </div>
  );
};
```
Example JSON response from **backend API**:
```json
{
  "id": 1,
  "name": {
    "en": "Wireless Headphones",
    "jp": "ワイヤレスヘッドホン",
    "ru": "Беспроводные наушники"
  },
  "description": {
    "en": "High-quality sound",
    "jp": "高品質の音",
    "ru": "Звук высокого качества"
  }
}
```

---

## **Alternative: Using Next.js for Server-Side Rendering**
If you need **SEO optimization**, consider **Next.js with `next-i18next`** for **server-side translations**.

### **Install Dependencies**
```sh
npm install next-i18next react-i18next i18next
```

### **Add `next-i18next.config.js`**
```javascript
module.exports = {
  i18n: {
    locales: ["en", "jp", "ru"],
    defaultLocale: "en",
  },
};
```

### **Modify `pages/_app.js`**
```javascript
import { appWithTranslation } from "next-i18next";
import "../styles/globals.css";

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

export default appWithTranslation(MyApp);
```

---

## **Final Thoughts**
✅ **Use `react-i18next` for client-side translations**  
✅ **Use `next-i18next` for server-side rendering (SEO)**  
✅ **Save user language preference in `localStorage` or `cookies`**  
✅ **Format dates & currencies dynamically using `Intl.NumberFormat`**  
✅ **Handle translations for backend API data dynamically**  

This setup ensures your **eCommerce** React app **supports multiple languages**, **remembers user preferences**, and **loads translations efficiently**. 🚀