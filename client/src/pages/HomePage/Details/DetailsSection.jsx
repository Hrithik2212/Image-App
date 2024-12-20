import ImageView from '@/components/ImageView/ImageView'
import React, { useEffect, useState } from 'react'
import ProductCard from '@/components/ProductCard/ProductCard';
import BASE_URL from '../../../utils/baseApi'
const DetailsSection = () => {
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
        const response = await fetch(BASE_URL+"/multi_image_ocr/", {
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
        setProductData(data);
        console.log(data)
      } catch (error) {
        console.error("Error uploading images:", error);
      }
      finally{
        setLoading(false)
      }
    };
    
    
    
    

    
  return (
    <div className='flex flex-col gap-8  h-fit justify-center items-center'>
      <div className='w-[80%] max-h-[500px] block max-w-[800px]  '>
        <ImageView mutiple={true} imgSrc={imagePreviews} loading={loading} handleImgUpload={handleImageUpload}/>
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
                             {productData?.estimated_shelf_life_days &&(
                                     <tr>
                                              <td>Estimated shelf life days</td>
                                              <td >{productData[index]?.estimated_shelf_life_days}</td> 
                                    </tr>
                                  )}
                                  {productData?.state &&(
                                     <tr>
                                              <td>State</td>
                                              <td className={`${productData[index]?.state ==="fresh" ?("text-green-500"):("text-red-500")}`}>{productData[index]?.state}</td> 
                                    </tr>
                                  )}
                                  {productData?.freshness &&(
                                     <tr>
                                              <td>Freshness</td>
                                              <td>{productData[index]?.freshness}</td> 
                                    </tr>
                                  )}

                         </tbody>
                         
                     </table>
                    )}
                </div>
            
            
        </React.Fragment>
        ):(
          loading ? (
            <div className='mx-auto mt-5 w-[25px] h-[25px] border-l-[2px] rounded-[20px] animate-spin  border-t-[2px] border-black'/>
            
          ):(
            <div className='w-full px-10 py-2'>
            <h2>Instructions:</h2>
            <ul  className="list-disc">
                <li>Upload multiple images of the same product from different angles.</li>
                <li>Each image should contain only one product.</li>
                <li>The system will extract text information (e.g., labels, specifications).</li>
                <li>View the consolidated OCR data in the results.</li>
            </ul>
            </div>
          )

      )}
      </div>

    </div>
  )
}

export default DetailsSection