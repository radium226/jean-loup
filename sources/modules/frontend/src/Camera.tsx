import { useState } from 'react'
import './App.css'

import { Client } from "./client"
import { toDataURL } from './utils'

import Spinner from './Spinner'
import Picture from './Picture'

export interface CameraProps {
    client: Client
}




function Camera ({ client }: CameraProps) {
    const [isTakingPicture, setIsTakingPicture] = useState(false)
    const [pictureSource, setPictureSource] = useState<string | null>(null)

    async function takePicture() {
        setIsTakingPicture(true)
        const picture = await client.takePicture()
        const blob = await client.downloadPictureContent(picture)
        const dataURL = await toDataURL(blob)
        setPictureSource(dataURL)
        setIsTakingPicture(false)
    }
    // { isTakingPicture ? ( <Spinner /> ) : ( <Picture source={ pictureSource } /> ) }
    return (
        <div className="flex-1 min-h-full flex flex-col items-stretch">
            <div className="flex-grow bg-white m-2 flex items-center justify-center">
                { isTakingPicture ? ( <Spinner /> ) : ( <Picture source={ pictureSource } /> ) }
            </div>
            <div>
                <button className="m-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={ takePicture }>📷 Prendre une photo ! </button>
            </div>
        </div>
    )

    /*

    <div className="h-full bg-red-800 sm:min-h-screen flex flex-col">
            <div className="flex-grow">
                <div>Coucou</div>
            </div>
            <div className="flex-shrink">
                <button className="m-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={ takePicture }>📷 Prendre une photo ! </button>
            </div>
        </div>

    */
}

export default Camera