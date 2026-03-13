import { useEffect, useState } from "react"

const API = "http://192.168.2.7:8000"

function Products() {

    const [products, setProducts] = useState([])

    const [name, setName] = useState("")
    const [description, setDescription] = useState("")
    const [price, setPrice] = useState("")
    const [stock, setStock] = useState("")

    const loadProducts = () => {
        fetch(API + "/products")
            .then(res => res.json())
            .then(data => setProducts(data))
    }

    useEffect(() => {
        loadProducts()
    }, [])

    const addProduct = async () => {

        await fetch(API + "/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name,
                description,
                price: Number(price),
                stock: Number(stock)
            })
        })

        setName("")
        setDescription("")
        setPrice("")
        setStock("")

        loadProducts()
    }

    const deleteProduct = async (id) => {

        await fetch(API + "/products/" + id, {
            method: "DELETE"
        })

        loadProducts()
    }

    return (

        <>
            <div className="topbar">
                Online Shop Admin
            </div>

            <div className="container">

                <h1>Products</h1>

                <div className="form">

                    <input placeholder="name" onChange={(e) => setName(e.target.value)} />

                    <input placeholder="description" onChange={(e) => setDescription(e.target.value)} />

                    <input placeholder="price" onChange={(e) => setPrice(e.target.value)} />

                    <input placeholder="stock" onChange={(e) => setStock(e.target.value)} />

                    <button onClick={addProduct}>Add product</button>

                </div>


                <div className="grid">

                    {products.map(p => (

                        <div className="card" key={p.id}>

                            <h3>{p.name}</h3>

                            <p>{p.description}</p>

                            <p><b>Price:</b> {p.price}</p>

                            <p><b>Stock:</b> {p.stock}</p>

                            <button
                                className="delete"
                                onClick={() => deleteProduct(p.id)}
                            >
                                Delete
                            </button>

                        </div>

                    ))}

                </div>

            </div>
        </>

    )
}

export default Products