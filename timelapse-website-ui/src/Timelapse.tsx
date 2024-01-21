import { Client } from "./client"

export interface TimelapseProps {
    client: Client

}

export default function Timelapse({ client }: TimelapseProps) {
    console.log(client)
    return (
        <>
            <h2>Timelapse</h2>
        </>
    )
}