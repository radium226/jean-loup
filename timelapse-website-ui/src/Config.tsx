import { Client } from "./client"
import { useState, useEffect } from "react"


export interface ConfigProps {

    client: Client,

}


export default function ConfigForm({ client }: ConfigProps) {

    const [wakeupTime, setWakeupTime] = useState<string | undefined>(undefined);
    const [isEnabled, setIsEnabled] =  useState<boolean>(false);

    useEffect(() => {
        ( async () => {
            const configValues = await client.readConfig()
            setWakeupTime(configValues.timeLapse.wakeupTime)
            setIsEnabled(configValues.timeLapse.enabled);
        })();
    }, [])


    return (
        <form onSubmit={ (event) => event.preventDefault() } className="flex flex-col w-full py-2 px-2">
            <fieldset className="border border-solid border-gray-300 p-3 mb-2 rounded-lg">
                <legend className="text-gray-500">Time Lapse</legend>
                
                <div className="flex-1 flex flex-col gap-2 justify-center">
                    <div className="flex-1 flex flex-col sm:flex-row items-center justify-center">
                        <label htmlFor="enabled" className="block w-full sm:w-1/6 text-center sm:text-right pr-2">Activé&nbsp;:&nbsp;</label>
                        <div className="flex-1 flex flex-col w-full sm:w-5/6 text-center sm:text-left sm:items-left items-center sm:items-start">
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input checked={ isEnabled } onChange={ (event) => setIsEnabled(event.target.checked) } id="enabled" type="checkbox" className="sr-only peer" />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                    </div>

                    <div className="flex-1 flex flex-col gap-2 justify-center">
                        <div className="flex-1 flex flex-col sm:flex-row items-center justify-center">
                            <label htmlFor="wakeupTime" className="block w-full sm:w-1/6 text-center sm:text-right pr-2">Heure de réveil&nbsp;:&nbsp;</label>
                            <div className="flex-1 flex flex-col w-full sm:w-5/6 text-center sm:text-left sm:items-left items-center sm:items-start">
                                <input type="text" value={ wakeupTime == undefined ? "" : wakeupTime } onChange={(event) => setWakeupTime(event.target.value)} id="wakeupTime" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" />
                            </div>
                        </div>
                    </div>
                </div>
            </fieldset>
            <button 
                type="submit" 
                onClick={ () => client.writeConfig({
                    timeLapse: {
                        wakeupTime: wakeupTime,
                        enabled: isEnabled,
                    }
                }) }
                className="mt-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
            >Sauvegarder</button>
        </form>
    )

}