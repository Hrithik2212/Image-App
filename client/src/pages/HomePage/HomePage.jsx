import React, { useState } from 'react';

import ImageSection from './Image/ImageSection';
import DetailsSection from './Details/DetailsSection';
import { Link } from 'react-router-dom';


const HomePage = () => {
  const [choice,setChoice]=useState(false)
  

    return(
      <React.Fragment>
        <nav className='w-full h-fit shadow-lg text-[var(--text-primary-color)] py-5 px-10  flex justify-between nav-shadow '>
      
            <section style={{"fontSize":"var(--secondary-font-size)"}} className='font-[var(--secondary-font-weight)] '>
                <Link to="/" className='flex gap-3 justify-center'>
                  <h1 className=''>FlipKart GRID</h1>
                </Link>
            </section>   
        </nav>
     
    
        <div className="min-h-full h-full  flex flex-col mt-5 ">
          <div className='w-fit  whitespace-nowrap  max-md:flex-col flex justify-center  mx-auto mb-5 shadow-lg  bg-white '>
            <button onClick={()=>setChoice(false)} className={`border-r w-full h-full py-2 px-2  ${!choice && ("bg-gray-300")}`}>
            Detect count and extract brand names
            </button>
            <button onClick={()=>setChoice(true)} className={`border-r w-full h-full py-2 px-2 ${choice && ("bg-gray-300")}`}>
              Extract OCR Information
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
  </React.Fragment>
    )

};

export default HomePage;
