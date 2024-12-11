import {createContext,useState,useEffect, useContext} from 'react'
import {Link, Outlet, useLocation, useNavigate} from 'react-router-dom'
import { jwtDecode } from "jwt-decode";
import { IoIosLogOut } from "react-icons/io";
import BASE_URL from '@/utils/baseApi';



const AuthContext = createContext()

export default AuthContext

export const AuthProvider = () =>{
    let  navigate= useNavigate();
    let [authToken,setAuthToken] = useState(()=> localStorage.getItem('authTokens') ? JSON.parse(localStorage.getItem('authTokens')) : null)
    let [user,setUser]= useState(()=> localStorage.getItem('authTokens') ? jwtDecode(localStorage.getItem('authTokens')) : null)
    const location = useLocation();
    const [loading, setLoading] = useState(true);
    

    
    


    const loginUser = async (e) =>{
        e.preventDefault()
        try{
            let response = await fetch(`${BASE_URL}token/`,{
                method:"POST",
                headers:{
                    'Content-Type':'application/json'
                },
                body: JSON.stringify({
                    email:e.target.email.value,
                    password:e.target.password.value
                })
               
            })
            let data = await response.json()
            if(response.status === 200){
                
                setAuthToken(data)
                localStorage.setItem('authTokens', JSON.stringify(data))
                setUser(jwtDecode(data.access_token))
                navigate('/');                
                
            }
            else{
                alert('credentials are wrong!')
            }
            
        }catch(err){
            console.log(err)
        }
    }
    useEffect(()=>{
        if(authToken){
            
        }else{
            navigate('/login');
        }
        
    },[user])
    const logoutUser = ()=>{
        setAuthToken(null)
        setUser(null)
        localStorage.removeItem('authTokens')
        navigate("/login")
    }
    const registerUser = async (e) =>{
        e.preventDefault();
        try{
            let  res=await fetch (`${BASE_URL}register/`, {
              method:'POST',
              headers:{'Content-type':'Application/json'},
              body: JSON.stringify({
                email:e.target.email.value,
                password:e.target.password.value,
              })
            })
           let data = await res.json()
           if(res.status===201){
                setAuthToken(data)
                localStorage.setItem('authTokens', JSON.stringify(data))
                setUser(jwtDecode(data.access))
                
                

           }else{
            alert("Somthing went to worng....")
           }

        }
        catch(err){
            console.log(err)
        }

    }
    let contextData={
        user:user,
        loginUser:loginUser,
        logoutUser:logoutUser,
        authToken:authToken,
        registerUser:registerUser
    }
    
    return(
        <AuthContext.Provider value={contextData}>
            <div className='h-full w-full '>
                <NavBar/>
                <div className='max-h-screen h-[90vh] w-full '>
                    <Outlet/>
                </div>
            </div>
        </AuthContext.Provider>
    )
}