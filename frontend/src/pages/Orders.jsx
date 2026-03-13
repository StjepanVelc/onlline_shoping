import { useState } from "react"

const API = "http://192.168.2.7:8000"

function Orders() {

    const [userId, setUserId] = useState("")
    const [productId, setProductId] = useState("")
    const [quantity, setQuantity] = useState("")
    const [address, setAddress] = useState("")

    const createOrder = async () => {

        await fetch(API + "/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: Number(userId),
                address: address,
                items: [
                    {
                        product_id: Number(productId),
                        quantity: Number(quantity)
                    }
                ]
            })
        })

        alert("Order created")

    }

    return (

        <div style={{ padding: "40px" }}>

            <h1>Create order</h1>

            <input placeholder="user id" onChange={(e) => setUserId(e.target.value)} />

            <input placeholder="product id" onChange={(e) => setProductId(e.target.value)} />

            <input placeholder="quantity" onChange={(e) => setQuantity(e.target.value)} />

            <input placeholder="address" onChange={(e) => setAddress(e.target.value)} />

            <button onClick={createOrder}>Create order</button>

        </div>

    )

}

export default Orders