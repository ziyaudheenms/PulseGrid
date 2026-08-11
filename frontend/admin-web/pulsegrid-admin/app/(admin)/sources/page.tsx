"use client"
import React from "react"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { useAppDispatch, useAppSelector } from "@/lib/redux/hook"
import { createSource, updateCreateStore, removeTheCreateStoreSource } from "@/features/sourceSlice"
import { source_scope } from "@/types/source"
import {
  IconFoldDown,
  IconGlobe,
  IconHome,
  IconList,
  IconUpload,
  IconWorld,
  IconWorldSearch,
  IconX,
} from "@tabler/icons-react"
import { useAuth } from "@clerk/nextjs"
import { Spinner } from "@/components/ui/spinner"
import { AsciiArt } from "@/components/ui/ascii-art"

function Page() {
  // state configs to collect the most and essential state data
  const [newSource, setNewSource] = useState({
    source_name: '',
    source_url: '',
    source_type: '',
    source_nationality: '',
    source_scope: 'Technical',
  })

  const { getToken } = useAuth()
  // managing using redux toolkit
  const { createSources } = useAppSelector(state => state.source)
  const dispatch = useAppDispatch()

  const handleSourceAddition = (e) => {
    e.preventDefault()
    dispatch(updateCreateStore(  //dispatch funtion is used to tigger the functions defined inside the state to update the state variables
      {
        sourceDetails: newSource
      }
    ))

    //Cleaning the input fields after its upload function
    setNewSource({
      source_name: '',
      source_url: '',
      source_type: '',
      source_nationality: '',
      source_scope: 'Technical',
    })
  }

  const uploadTheSources = async (e) => {
    e.preventDefault()
    const clerkJwtToken = await getToken()

    dispatch(
      createSource({
        token: clerkJwtToken || ''
      })
    )
  }

  const handleRemoveSource = (index: any) => {
    dispatch(removeTheCreateStoreSource({ index }))
  }


  return (
    <div className="mx-auto flex items-center justify-center md:justify-between gap-3 px-2 md:px-16">
      <div className="flex h-screen sm:w-full md:w-[48%] flex-col justify-center">
        <div className="my-14">
          <h1 className="text-4xl font-black font-serif tracking-tight italic">Add Sources</h1>
          <p className="text-lg font-medium text-slate-600 mt-2 max-w-xl leading-relaxed">
            Add new sources to fuel up the pulsegrid data pipeline.
          </p>
        </div>
        <div className="my-10 w-full md:w-[70%]">
          <div className="flex flex-col gap-4">
            {/* <div className="flex flex-col gap-2 w-full"> */}
              <div className="flex items-center w-full flex-row-reverse group">
               
                
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full transition-all duration-300 ease-in rounded-2xl py-5 peer"
                  placeholder="eg:- TechCrunch"
                  value={newSource.source_name}
                  onChange={(e) => setNewSource({ ...newSource, source_name: e.target.value })}
                />
                <div className="h-1 w-2 bg-secondary group-focus-within:opacity-0 transition-all duration-300 ease-in opacity-100">
                </div>
                 <div className="border-color-border flex h-11 w-12 items-center justify-center rounded-full border dark:bg-input/30 group-focus-within:translate-x-3 group-focus-within:scale-110 group-focus-within:rotate-[360deg] transition-all duration-300 ease-in">
                  <IconGlobe className="text-2xl" stroke={2} />
                </div>

              </div>
            {/* </div> */}
            {/* <div className="flex flex-col gap-2"> */}
              <div className="flex items-center flex-row-reverse group">
                
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full ease-in rounded-2xl py-5 peer"
                  placeholder="eg:- www.TechCrunch.com"
                  value={newSource.source_url}
                  onChange={(e) => setNewSource({ ...newSource, source_url: e.target.value })}
                />
                <div className="h-1 w-2 bg-secondary group-focus-within:opacity-0 transition-all duration-300 ease-in opacity-100">
                </div>
                  <div className="border-color-border flex h-11 w-12 items-center justify-center rounded-full border dark:bg-input/30 group-focus-within:translate-x-3 group-focus-within:scale-110 group-focus-within:rotate-[360deg] transition-all duration-300 ease-in">
                  <IconWorldSearch className="text-2xl" stroke={2} />
                </div>
               
              </div>
            {/* </div> */}
            {/* <div className="flex flex-col gap-2"> */}
              <div className="flex items-center flex-row group">
                <div className="border-color-border flex h-11 w-12 items-center justify-center rounded-full border dark:bg-input/30 group-focus-within:translate-x-3 group-focus-within:scale-110 group-focus-within:rotate-[360deg] transition-all duration-300 ease-in">
                  <IconWorld className="text-2xl" stroke={2} />
                </div>
               <div className="h-1 w-2 bg-secondary group-focus-within:opacity-0 transition-all duration-300 ease-in opacity-100">
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full transition-all duration-300 ease-in rounded-2xl py-5 peer"
                  placeholder="eg:- International or National"
                  value={newSource.source_type}
                  onChange={(e) => setNewSource({ ...newSource, source_type: e.target.value })}
                />
                
              </div>
            {/* </div> */}

            {/* <div className="flex flex-col gap-2"> */}
              <div className="flex items-center flex-row group">
                  <div className="border-color-border flex h-11 w-12 items-center justify-center rounded-full border dark:bg-input/30 group-focus-within:translate-x-3 group-focus-within:scale-110 group-focus-within:rotate-[360deg] transition-all duration-300 ease-in">
                  <IconHome className="text-2xl" stroke={2} />
                </div>
                <div className="h-1 w-2 bg-secondary group-focus-within:opacity-0 transition-all duration-300 ease-in opacity-100">
                </div>
                <Input
                  id="input-field-username"
                  type="text"
                  className="w-full transition-all duration-300 ease-in rounded-xl py-5 peer"
                  placeholder="eg:- India or America or Japan"
                  value={newSource.source_nationality}
                  onChange={(e) => setNewSource({ ...newSource, source_nationality: e.target.value })}
                />
              
              </div>
            {/* </div> */}

            {/* <div className="flex flex-col gap-2"> */}
              <div className="flex items-center flex-row group  ">
                <div className="border-color-border flex h-10 w-10 items-center justify-center rounded-full border dark:bg-input/30 group-focus-within:translate-x-3 group-focus-within:scale-110 group-focus-within:rotate-[360deg] transition-all duration-300 ease-in">
                  <IconFoldDown className="text-2xl" stroke={2} />
                </div>
               <div className="h-1 w-2 bg-secondary group-focus-within:opacity-0 transition-all duration-300 ease-in opacity-100">
                </div>
                <DropdownMenu >
                  <DropdownMenuTrigger render={<Button variant="outline" className={"w-[88%] text-left peer"} />} className={"text-left"}>
                    {newSource.source_scope}
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Technical' })
                      }}>Technical</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Gaming' })
                      }}>Gaming</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setNewSource({ ...newSource, source_scope: 'Cinema' })
                      }}>Cinema</DropdownMenuItem>
                    </DropdownMenuGroup>
                  </DropdownMenuContent>
                </DropdownMenu>
                
              </div>
            {/* </div> */}

          </div>
          <div className="w-[50%] flex items-center justify-between gap-1">
            <Button className="mt-5  hover:brightness-125 flex w-full items-center gap-2 py-5 group  transition-all duration-300 ease-in hover:scale-95" onClick={(e) => handleSourceAddition(e)}>
              <IconList stroke={2} className="text-xl group-hover:translate-y-[-1px] group-hover:scale-150 transition-transform duration-300" />
              Add Source To The List
            </Button>

            <Button className="mt-5 flex w-full items-center gap-2 py-5 dark:bg-sidebar-accent bg-destructive group-hover:dark:bg-destructive hover:scale-95 transition-all duration-300 ease-in" onClick={(e) => uploadTheSources(e)}>
              {
                createSources.isLoading ? <Spinner className="text-primary" /> : <IconUpload stroke={2} className="text-xl" />
              }

              Upload The Source
            </Button>
          </div>
        </div>
        <div className=" flex flex-col items-center gap-2 w-[68%] h-48 overflow-y-scroll no-scrollbar ">
          {
            createSources.data.map((source, index) => (
              <div key={index} className="flex items-center gap-2 w-full  justify-between">
                <DropdownMenu key={index}>
                  <DropdownMenuTrigger render={<Button className={"w-[88%]"} variant="secondary" />}>
                    {
                      source.source_name
                    }
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuGroup>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Source: </span>{source.source_name}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">URL: </span>{source.source_url}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Type: </span>{source.source_type}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Nationality: </span>{source.source_nationality}</DropdownMenuItem>
                      <DropdownMenuItem><span className="font-medium text-l font-sans text-destructive">Scope: </span>{source.source_scope}</DropdownMenuItem>
                    </DropdownMenuGroup>
                  </DropdownMenuContent>
                </DropdownMenu>
                <div className="flex items-center gap-2">
                  <div className="py-1 px-2 rounded-xl bg-sidebar-accent hover:scale-90  transition-all duration-300 ease-in" onClick={() => {
                    handleRemoveSource(index)
                  }}>
                    <IconX className="text-destructive" stroke={2} />
                  </div>
                </div>
              </div>
            ))
          }
        </div>
      </div>
      <div className="group">
        <AsciiArt 
        src="/logo.png"
        resolution={100}
        color="var(--color-neutral-500)"
        animationStyle="fade"
        animationDuration={1.5}
        animateOnView={false}
        className="mx-auto aspect-square w-full max-w-lg bg-neutral-950 group-hover:hidden transition-all duration-300 ease-in"
        />
        <img src="/logo.png" alt="sources" className="hidden opacity-0 group-hover:block group-hover:opacity-100 animate-in transition-all duration-700 ease-in-out" />
      </div>
    </div>
  )
}

export default Page
