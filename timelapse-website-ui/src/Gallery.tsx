import { Client } from "./client"

export interface GalleryProps {
    client: Client

}

export default function Gallery({ client }: GalleryProps) {
    console.log(client)
    return (
        <>
            <h2>Gallery</h2>
        </>
    )
}