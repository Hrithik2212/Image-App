import { createBrowserRouter, RouterProvider,Link } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage/HomePage'


function App() {
  const router = createBrowserRouter([
    {
      path: '/',
      children: [
        {
          path: '/home',
          element: <HomePage />
        },
      ]

    }
  ])

  return (
   
    <RouterProvider router={router} />
    
  )
}

export default App
