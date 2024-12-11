import ImageView from '@/components/ImageView/ImageView'
import React, { useEffect, useState } from 'react'
import ProductCard from '@/components/ProductCard/ProductCard';
const ImageSection = () => {

    const [productData,setProductData]=useState(null)
    const [imagePreviews, setImagePreviews] = useState(null);
    const [loading,setLoading]=useState(false)
    const [show,setShow]=useState(null)

  
    const handleImageUpload = async (e) => {
      const files = Array.from(e.target.files);
    
      const base64Images = await Promise.all(
        files.map((file) => {
          return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = () => reject(new Error("Failed to read file"));
            reader.readAsDataURL(file); 
          });
        })
      );
      setImagePreviews(base64Images); 
    
      sendImagesToBackend(base64Images);
    };
    
    const sendImagesToBackend = async (base64Images) => {
      try {
        setLoading(true)
        const response = await fetch("http://localhost:8000/analyze_group/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ image: base64Images[0] }),
        });
    
        if (!response.ok) {
          throw new Error("Failed to upload images");
        }
    
        const data = await response.json();
        setProductData(data);
      } catch (error) {
        console.error("Error uploading images:", error);
      }
      finally{
        setLoading(false)
      }
    };

  return (
    <div className='flex flex-col  h-fit justify-center items-center'>
      <div className='w-[80%] max-h-[500px] block max-w-[800px]  '>
        <ImageView mutiple={false} imgSrc={imagePreviews} loading={loading} handleImgUpload={handleImageUpload}/>
      </div>
      <div className='shadow-lg pb-5 w-[80%] md:max-w-[70vw] mx-auto   h-fit my-5 overflow-y-scroll  bg-white'>
        {productData ? (
            <React.Fragment>
          
        
                <div className='w-full cursor-pointer border-b' >
                    {productData.map((product,index)=>(
                      <div className='w-full cursor-pointer border-b' onClick={()=>setShow(index)} key={index}>
                      <ProductCard  product={product} />
                      {show===index && (
                          <table className=' mx-auto gap-2 m-5 w-[80%]  '>
                              <thead>
                                  <tr>
                                      <th>Info</th>
                                      <th>Value</th>
                                  </tr>
                              </thead>
                              <tbody>
                                  {productData[index]?.brand_name &&(
                                    <tr>
                                              <td>Brandname</td>
                                              <td>{productData[index]?.brand_name}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.brand_details &&(
                                     <tr>
                                      <td>Brand Details</td>
                                      <td>{productData[index]?.brand_details}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.Logo &&(
                                     <tr>
                                        <td>Logo</td>
                                        <td>{productData[index]?.Logo}</td> 
                                      </tr>
                                  )}
                                  {productData[index]?.product_name &&(
                                     <tr>
                                        <td>Product Name</td>
                                        <td>{productData[index]?.product_name}</td> 
                                      </tr>
                                  )}
                                  {productData[index]?.item_count &&(
                                     <tr>
                                        <td>Item Count</td>
                                        <td>{productData[index]?.item_count}</td> 
                                      </tr>
                                  )}
                                  {productData[index]?.pack_size &&(
                                      <tr>
                                                <td>Pack Size</td>
                                                <td>{productData[index]?.pack_size}</td> 
                                      </tr>
                                  )}
                                  {productData[index]?.expiry_date &&(
                                     <tr>
                                              <td>Expiry Date</td>
                                              <td>{productData[index]?.expiry_date}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.mrp &&(
                                     <tr>
                                              <td>MRP</td>
                                              <td>{productData[index]?.mrp}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.category &&(
                                     <tr>
                                              <td>Category</td>
                                              <td>{productData[index]?.category}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.estimated_shelf_life_days &&(
                                     <tr>
                                              <td>State</td>
                                              <td className={`${productData[index]?.estimated_shelf_life_days ==="fresh" ?("text-green-500"):("text-red-500")}`}>{productData[index]?.estimated_shelf_life_days}</td> 
                                    </tr>
                                  )}
                                  {productData[index]?.state &&(
                                     <tr>
                                              <td>State</td>
                                              <td className={`${productData[index]?.state ==="fresh" ?("text-green-500"):("text-red-500")}`}>{productData[index]?.state}</td> 
                                    </tr>
                                  )}
                              </tbody>
                              
                          </table>
                      )}
                  </div>
              ))}
               
                </div>
            
            
        </React.Fragment>
        ):(
            loading ? (
              <div className='mx-auto mt-5 w-[25px] h-[25px] border-l-[2px] rounded-[20px] animate-spin  border-t-[2px] border-black'/>
              
            ):(
              <div className='w-full'>
                  <h4 className='w-full h-full flex justify-center items-center px-5 py-2 text-[20px] text-center'>Welcome<br></br> to Team Sentinels at Flipkart Grid Hackathon!</h4>
              </div>
            )

        )}
      </div>

    </div>
  )
}

export default ImageSection