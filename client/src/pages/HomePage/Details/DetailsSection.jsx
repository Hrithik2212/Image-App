import ImageView from '@/components/ImageView/ImageView'
import React, { useEffect, useState } from 'react'
import ProductCard from '@/components/ProductCard/ProductCard';
import data from '../Sample_Response'
const DetailsSection = () => {
  const [productData,setProductData]=useState(data.products[0])
    const [imagePreviews, setImagePreviews] = useState(null);
    const [loading,setLoading]=useState(false)
    const [show,setShow]=useState(null)
    const [processedImages, setProcessedImages] = useState([]);

  
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
        const response = await fetch("http://localhost:8000/upload-image/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ images: base64Images }),
        });
    
        if (!response.ok) {
          throw new Error("Failed to upload images");
        }
    
        const data = await response.json();
        setProcessedImages(data.base64);
        console.log(data.base64)
      } catch (error) {
        console.error("Error uploading images:", error);
      }
    };
    
    
    
    

    
  return (
    <div className='flex flex-col gap-10 h-fit justify-center items-center'>
      <div className='w-[80%] max-h-[500px] block max-w-[800px]  '>
        <ImageView  imgSrc={imagePreviews} loading={loading} handleImgUpload={handleImageUpload}/>
      </div>
      <div className='shadow-lg pb-5 w-[80%] md:max-w-[70vw] mx-auto   h-fit my-5 overflow-y-scroll  bg-white'>
        {productData ? (
            <React.Fragment>
          
        
                <div className='w-full cursor-pointer border-b' onClick={()=>setShow(!show)} >
                    <ProductCard  product={productData} />
                    {show && (
                         <table className=' mx-auto gap-2 m-5 w-[80%]  '>
                         <thead>
                             <tr>
                                 <th>Info</th>
                                 <th>Value</th>
                             </tr>
                         </thead>
                         <tbody>
                             {productData?.track_id &&(
                               <tr>
                                         <td>Tracker Id</td>
                                         <td>{productData?.track_id}</td> 
                               </tr>
                             )}
                             {productData?.product_name &&(
                                <tr>
                                 <td>Class Name</td>
                                 <td>{productData?.product_name}</td> 
                               </tr>
                             )}
                             {productData?.category &&(
                                <tr>
                                   <td>Category</td>
                                   <td>{productData?.category}</td> 
                                 </tr>
                             )}
                             {productData?.brand_name &&(
                                <tr>
                                   <td>Brand Name</td>
                                   <td>{productData?.brand_name}</td> 
                                 </tr>
                             )}
                             {productData?.brand_details &&(
                                <tr>
                                   <td>Brand Details</td>
                                   <td>{productData?.brand_details}</td> 
                                 </tr>
                             )}
                             {productData?.pack_size &&(
                                 <tr>
                                           <td>Pack Size</td>
                                           <td>{productData?.pack_size}</td> 
                                 </tr>
                             )}
                             {productData?.expiry_date &&(
                                <tr>
                                         <td>Expiry Date</td>
                                         <td>{productData?.expiry_date}</td> 
                               </tr>
                             )}
                             {productData?.mrp &&(
                                <tr>
                                         <td>MRP</td>
                                         <td>{productData?.mrp}</td> 
                               </tr>
                             )}
                             {productData?.state &&(
                                <tr>
                                         <td>State</td>
                                         <td className={`${productData?.state ==="fresh" ?("bg-green-700 fonfont-t-bold"):("bg-red-500 bold")}`}></td> 
                               </tr>
                             )}

                         </tbody>
                         
                     </table>
                    )}
                </div>
            
            
        </React.Fragment>
        ):(
            <div className='w-full'>
                <h4 className='w-full h-full flex justify-center items-center px-5 py-2 text-[20px] text-center'>Welcome<br></br> to Team Sentinels at Flipkart Grid Hackathon!</h4>
            </div>

        )}
      </div>

    </div>
  )
}

export default DetailsSection