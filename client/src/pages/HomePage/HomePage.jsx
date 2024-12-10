import React, { useState } from 'react';

import ImageSection from './Image/ImageSection';
import DetailsSection from './Details/DetailsSection';


const HomePage = () => {
  const [choice,setChoice]=useState(false)
  

    return(
    
  <div className="min-h-full h-full  flex flex-col mt-5 ">
    <div className='w-[150px] flex justify-center  mx-auto mb-5 shadow-lg  bg-white '>
      <button onClick={()=>setChoice(false)} className={`border-r w-full h-full py-2  ${!choice && ("bg-gray-300")}`}>
      Image
      </button>
      <button onClick={()=>setChoice(true)} className={`border-r w-full h-full py-2  ${choice && ("bg-gray-300")}`}>
        Deatails
      </button>
    </div>
    {choice ? (
      <div className='h-full w-full'>
         <DetailsSection/>
      </div>
    ):(
      <div className='h-full w-full'>
        <ImageSection/> 
         
         
      </div>
    )}
    
   
  </div>
    )
};

export default HomePage;
