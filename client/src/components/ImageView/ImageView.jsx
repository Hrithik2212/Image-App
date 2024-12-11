import React from 'react';
import { Slide } from 'react-slideshow-image';
import 'react-slideshow-image/dist/styles.css'



const ImageView = ({ imgSrc, loading, handleImgUpload ,mutiple}) => {
  return (
    <div className="relative flex h-full  w-full items-center justify-center bg-transparent overflow-hidden">
      {imgSrc && imgSrc.length > 0 ? (
        <div className="w-full h-fit relative ">
                  <div className=''>
                          {imgSrc.length>1 ?(
                            <Slide>
                            {imgSrc.map((slideImage, index)=> (
                                <div  key={index}>
                                  <img alt={`image-${index}`} className='h-fit w-full max-h-[500px] object-contain' src={slideImage}/>
                                </div>
                              ))} 
                            </Slide>
                          ):(
                            imgSrc.map((slideImage, index)=> (
                              <div  key={index}>
                                <img alt={`image-${index}`} className='h-fit w-full max-h-[500px] object-contain' src={slideImage}/>
                              </div>
                            ))
                          )}
                    </div>
                    <div className='py-2 border cursor-pointer shadow-2xl relative flex justify-center items-center bg-white'>
                        <label htmlFor="file" className='text-black text-center  mx-auto font-bold'>Re-Upload Image</label>
                        <input className='opacity-0 absolute w-full h-full cursor-pointer'  name="file"  onClick={()=>{window.location.reload()}} />
                    </div>

        </div>
        
       
      ) : (
        <div className='w-full relative  h-full flex flex-col'>
          {loading ? (
            <div className='z-0 absolute flex justify-center items-center cursor-wait w-full h-full'>
              <div className='bg-gray-50 absolute opacity-[0.3] w-full h-full' />
              <div className='w-[40px] cursor-wait h-[40px] border-white opacity-1 z-10 border-l-0 border-t-0 animate-spin border-2 rounded-full bg-transparent' />
            </div>
          ) : (
            <div className='absolute w-full h-full text-white flex justify-center items-center'>
              <h4 className='w-full text-center mx-auto font-bold'>Upload Image</h4>
              <input className='absolute cursor-pointer w-full h-full opacity-0' type="file" accept="image/*" multiple={mutiple}  onChange={handleImgUpload} />
            </div>
          )}
          <img className="h-full w-full max-h-[500px]" src='https://assets.timelinedaily.com/j/1203x902/2024/07/flipkart.jpg' />
        </div>
      )}
    </div>
  );
};

export default ImageView;
