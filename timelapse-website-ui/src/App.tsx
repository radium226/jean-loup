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
import Config from "./Config"



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
          path: "/timeLapse",
          element: <Timelapse client={ client } />,
        },
        {
          path: "/gallery",
          element: <Gallery client={ client } />,
        },
        {
          path: "/config",
          element: <Config client={ client } />,
        }
      ]
    },
  ]);
  return <RouterProvider router={router} />
}

export default App
