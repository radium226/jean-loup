export class Client {

    async takePicture(): Promise<Blob> {
        const response = await fetch("/api/pictures", {
            method: "POST",
        })
        const blob = await response.blob()
        return blob;
    }
    
}