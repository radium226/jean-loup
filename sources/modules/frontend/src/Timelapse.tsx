import { Client } from "./client"

export interface TimelapseProps {
    client: Client

}

export default function Timelapse({ client }: TimelapseProps) {
    console.log(client)
    return (
        <div className="w-full h-full bg-red-100 flex flex-col items-center justify-center">
            <video className="h-full w-full rounded-lg" controls>
                <source src="/api/timeLapse" type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    )
}