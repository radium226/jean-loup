import './App.css'
import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom"

import Layout from "./Layout"
import { Client } from './client'
import Camera from "./Camera"
import Timelapse from './Timelapse'
import Gallery from './Gallery'



function App() {
  const client = new Client()
  const router = createBrowserRouter([
    {
      path: "/",
      element: (
        <Layout>
          <Outlet />
        </Layout>
      ),
      children: [
        {
          path: "/camera",
          element: <Camera client={ client } />,
        },
        {
          path: "/timelapse",
          element: <Timelapse client={ client } />,
        },
        {
          path: "/gallery",
          element: <Gallery client={ client } />,
        }
      ]
    },
  ]);
  return <RouterProvider router={router} />
}

export default App
