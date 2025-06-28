Thanks for sharing the photo of your notes. Here's a clean and structured transcription of the content you wrote:

---

### 📦 Product Images

* `ProductImage` will hold **multiple images per product** for multiple reasons.
* It will have a **foreign key pointing to a Product**.
* It will have an **image field** and a **"tag" field** to specify the purpose of the image.

  * For example, `"icon"` will be used to render product images inside a `DataTable` grid.

---

### 🛒 DataTable with AddToCart Button

* When I press on **AddToCart**, it takes me to a page where:

  * I specify the **quantity**
  * Press **Add**, which should take me to a **Shopping Cart** page that shows:

    * Products
    * Their corresponding **quantities** in my shopping cart.

* I can either leverage:

  * **localStorage**
  * or a **database** to store products in my cart.

---

### 🔄 Cart Management

* I should have the ability to:

  * **Change quantities** of products in my cart
  * Or **remove** them from the cart altogether.

---

### 🧾 Order Flow

* Once I am ready to order items in my cart:

  * I press **“Buy”**, which will take me to a **confirmation page**
  * I press **“Buy”** again to actually buy
  * On the confirmation page, I will **choose payment method**

---

### 👤 Customer vs Admin Views

* I should be able to **check my orders** from an **Orders page**.

  * This will be different from the **Admin Order page** where:

    * Admin will have the ability to **check all orders across all customers**.

---

Would you like me to turn this into an implementation checklist or user stories for development?
