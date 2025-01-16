export function toDataURL(blob: Blob): Promise<string> {
    return new Promise((onSuccess, onError) => {
        try {
            const reader = new FileReader()
            reader.onload = () => {
            const base64 = reader.result as string
            onSuccess(base64)
        }
            reader.readAsDataURL(blob)
        } catch(e) {
            onError(e)
        }
    })
}