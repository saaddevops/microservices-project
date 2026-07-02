import { useEffect, useState } from "react";

function App() {

  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  const [isRegister, setIsRegister] =
    useState(false);

  const [username, setUsername] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [productName, setProductName] =
    useState("");

  const [quantity, setQuantity] =
    useState("");

  const [orders, setOrders] =
    useState([]);

  const register = async () => {

    try {

      const response = await fetch(
        "http://localhost:8000/register",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            username,
            email,
            password
          })
        }
      );

      const data =
        await response.json();

      alert(data.message);

      if (response.ok) {

        setIsRegister(false);

        setUsername("");
        setEmail("");
        setPassword("");
      }

    } catch (error) {

      console.error(error);

      alert(
        "Registration Failed"
      );
    }
  };

  const login = async () => {

    try {

      const response = await fetch(
        "http://localhost:8000/login",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            email,
            password
          })
        }
      );

      const data =
        await response.json();

      if (data.token) {

        localStorage.setItem(
          "token",
          data.token
        );

        setToken(data.token);

        alert(
          "Login Successful"
        );

      } else {

        alert(data.message);
      }

    } catch (error) {

      console.error(error);

      alert("Login Failed");
    }
  };

  const createOrder =
    async () => {

      try {

        const response =
          await fetch(
            "http://localhost:8000/orders",
            {
              method: "POST",

              headers: {

                "Content-Type":
                  "application/json",

                Authorization:
                  `Bearer ${token}`
              },

              body: JSON.stringify({
                product_name:
                  productName,

                quantity:
                  Number(quantity)
              })
            }
          );

        const data =
          await response.json();

        alert(data.message);

        loadOrders();

        setProductName("");
        setQuantity("");

      } catch (error) {

        console.error(error);

        alert(
          "Failed to create order"
        );
      }
    };

  const loadOrders =
    async () => {

      try {

        const response =
          await fetch(
            "http://localhost:8000/orders",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        const data =
          await response.json();

        setOrders(data);

      } catch (error) {

        console.error(error);

        alert(
          "Failed to load orders"
        );
      }
    };

  const logout = () => {

    localStorage.removeItem(
      "token"
    );

    setToken(null);

    setOrders([]);
  };

  useEffect(() => {

    if (token) {

      loadOrders();
    }

  }, [token]);

  if (!token) {

    return (

      <div
        style={{
          padding: "30px"
        }}
      >

        <h1>
          {isRegister
            ? "Register"
            : "Login"}
        </h1>

        {isRegister && (

          <>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) =>
                setUsername(
                  e.target.value
                )
              }
            />

            <br />
            <br />
          </>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
        />

        <br />
        <br />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <br />
        <br />

        {isRegister ? (

          <button
            onClick={register}
          >
            Register
          </button>

        ) : (

          <button
            onClick={login}
          >
            Login
          </button>

        )}

        <br />
        <br />

        <button
          onClick={() =>
            setIsRegister(
              !isRegister
            )
          }
        >
          {isRegister
            ? "Already have an account?"
            : "Create Account"}
        </button>

      </div>
    );
  }

  return (

    <div
      style={{
        padding: "30px"
      }}
    >

      <h1>
        Order Dashboard
      </h1>

      <button
        onClick={logout}
      >
        Logout
      </button>

      <hr />

      <h2>
        Create Order
      </h2>

      <input
        type="text"
        placeholder="Product Name"
        value={productName}
        onChange={(e) =>
          setProductName(
            e.target.value
          )
        }
      />

      <br />
      <br />

      <input
        type="number"
        placeholder="Quantity"
        value={quantity}
        onChange={(e) =>
          setQuantity(
            e.target.value
          )
        }
      />

      <br />
      <br />

      <button
        onClick={createOrder}
      >
        Create Order
      </button>

      <hr />

      <h2>
        My Orders
      </h2>

      <button
        onClick={loadOrders}
      >
        Refresh Orders
      </button>

      <ul>

        {orders.map(
          (order) => (

            <li
              key={order.id}
            >
              {order.product_name}
              {" - Qty: "}
              {order.quantity}
            </li>
          )
        )}

      </ul>

    </div>
  );
}

export default App;