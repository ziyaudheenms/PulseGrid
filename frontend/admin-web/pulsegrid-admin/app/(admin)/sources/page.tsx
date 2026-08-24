"use client"
import React, { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import { Field, FieldLabel, FieldDescription } from "@/components/ui/field"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"

import { useAppDispatch, useAppSelector } from "@/lib/redux/hook"
import { createSource, updateCreateStore, removeTheCreateStoreSource } from "@/features/sourceSlice"
import { useAuth, UserButton } from "@clerk/nextjs"
import { Spinner } from "@/components/ui/spinner"
import {
  Globe,
  Link2,
  Home,
  Plus,
  Upload,
  X,
  Code,
  Gamepad2,
  Film,
  RefreshCw,
  Layers,
  ChevronDown,
} from "lucide-react"

function Page() {
  const [newSource, setNewSource] = useState<{
    source_name: string
    source_url: string
    source_type: string
    source_nationality: string
    source_scope: "Technical" | "Gaming" | "Cinema"
  }>({
    source_name: "",
    source_url: "",
    source_type: "",
    source_nationality: "",
    source_scope: "Technical",
  })

  const { getToken } = useAuth()
  const { createSources } = useAppSelector((state) => state.source)
  const dispatch = useAppDispatch()

  const handleSourceAddition = (e: React.FormEvent) => {
    e.preventDefault()

    dispatch(
      updateCreateStore({
        sourceDetails: newSource,
      })
    )

    // Cleaning the input fields after upload function
    setNewSource({
      source_name: "",
      source_url: "",
      source_type: "",
      source_nationality: "",
      source_scope: "Technical",
    })
  }

  const uploadTheSources = async (e: React.FormEvent) => {
    e.preventDefault()
    const clerkJwtToken = await getToken()

    dispatch(
      createSource({
        token: clerkJwtToken || "",
      })
    )
  }

  const handleRemoveSource = (index: number) => {
    dispatch(removeTheCreateStoreSource({ index }))
  }

  return (
    <div className="min-h-screen bg-linear-to-b from-background to-muted/20 text-foreground pb-12">
      {/* Admin Dashboard Control Bar */}
      <header className="border-b border-border bg-card/60 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center shadow-md shadow-primary/20">
            <img src="/logo.png" alt="PulseGrid Logo" className="h-6 w-6 invert-0 dark:invert" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading font-bold text-lg tracking-tight">PulseGrid</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium border border-primary/20">
                Admin
              </span>
            </div>
            <p className="text-[10px] text-muted-foreground -mt-0.5">Control Center</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
            <span>Infrastructure</span>
            <span>/</span>
            <span className="text-foreground">Ingestion Sources</span>
          </div>
          <UserButton />
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-4 md:px-8 mt-8">
        {/* Page Title Block */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl font-bold tracking-tight">Ingestion Pipeline Configuration</h1>
            <p className="text-muted-foreground mt-1 max-w-2xl text-sm leading-relaxed">
              Register, validate, and manage ingestion feeds to fuel up the PulseGrid data pipeline.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-card border border-border rounded-xl p-3 shadow-xs">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0">
              <RefreshCw className="size-5 animate-spin duration-3000" />
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">
                Pipeline Status
              </p>
              <p className="text-xs font-bold text-emerald-500">Ingestion Active</p>
            </div>
          </div>
        </div>

        {/* Dashboard Panels Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Form Configurator */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            <div className="rounded-xl border border-border bg-card shadow-xs p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

              <div className="mb-6">
                <h2 className="font-heading text-xl font-semibold">Register Ingestion Source</h2>
                <p className="text-xs text-muted-foreground mt-1">
                  Configure details for a new RSS feed or news website
                </p>
              </div>

              <form onSubmit={handleSourceAddition} className="flex flex-col gap-5">
                {/* Source Name */}
                <Field>
                  <FieldLabel
                    htmlFor="source_name"
                    className="text-xs uppercase tracking-wider font-semibold text-muted-foreground"
                  >
                    Source Name
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupAddon align="inline-start">
                      <Globe className="size-4 text-muted-foreground/75" />
                    </InputGroupAddon>
                    <InputGroupInput
                      id="source_name"
                      placeholder="eg:- TechCrunch"
                      value={newSource.source_name}
                      onChange={(e) => setNewSource({ ...newSource, source_name: e.target.value })}
                    />
                  </InputGroup>
                </Field>

                {/* Source URL */}
                <Field>
                  <FieldLabel
                    htmlFor="source_url"
                    className="text-xs uppercase tracking-wider font-semibold text-muted-foreground"
                  >
                    Source URL
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupAddon align="inline-start">
                      <Link2 className="size-4 text-muted-foreground/75" />
                    </InputGroupAddon>
                    <InputGroupInput
                      id="source_url"
                      placeholder="eg:- www.TechCrunch.com"
                      value={newSource.source_url}
                      onChange={(e) => setNewSource({ ...newSource, source_url: e.target.value })}
                    />
                  </InputGroup>
                </Field>

                {/* Source Type & Nationality */}
                <div className="grid grid-cols-2 gap-4">
                  <Field>
                    <FieldLabel
                      htmlFor="source_type"
                      className="text-xs uppercase tracking-wider font-semibold text-muted-foreground"
                    >
                      Type
                    </FieldLabel>
                    <InputGroup>
                      <InputGroupAddon align="inline-start">
                        <Globe className="size-4 text-muted-foreground/75" />
                      </InputGroupAddon>
                      <InputGroupInput
                        id="source_type"
                        placeholder="eg:- International or National"
                        value={newSource.source_type}
                        onChange={(e) => setNewSource({ ...newSource, source_type: e.target.value })}
                      />
                    </InputGroup>
                  </Field>

                  <Field>
                    <FieldLabel
                      htmlFor="source_nationality"
                      className="text-xs uppercase tracking-wider font-semibold text-muted-foreground"
                    >
                      Nationality
                    </FieldLabel>
                    <InputGroup>
                      <InputGroupAddon align="inline-start">
                        <Home className="size-4 text-muted-foreground/75" />
                      </InputGroupAddon>
                      <InputGroupInput
                        id="source_nationality"
                        placeholder="eg:- India or America or Japan"
                        value={newSource.source_nationality}
                        onChange={(e) =>
                          setNewSource({ ...newSource, source_nationality: e.target.value })
                        }
                      />
                    </InputGroup>
                  </Field>
                </div>

                {/* Source Scope Selection cards */}
                <Field className="mt-2">
                  <FieldLabel className="text-xs uppercase tracking-wider font-semibold text-muted-foreground">
                    Source Scope
                  </FieldLabel>
                  <div className="grid grid-cols-3 gap-2 mt-1">
                    {[
                      {
                        id: "Technical",
                        label: "Technical",
                        icon: Code,
                        desc: "Tech & Dev",
                        color: "hover:border-blue-500/50 hover:bg-blue-500/5",
                        activeColor:
                          "border-blue-500 bg-blue-500/10 text-blue-500 dark:border-blue-400 dark:text-blue-400",
                      },
                      {
                        id: "Gaming",
                        label: "Gaming",
                        icon: Gamepad2,
                        desc: "Games & Esports",
                        color: "hover:border-emerald-500/50 hover:bg-emerald-500/5",
                        activeColor:
                          "border-emerald-500 bg-emerald-500/10 text-emerald-500 dark:border-emerald-400 dark:text-emerald-400",
                      },
                      {
                        id: "Cinema",
                        label: "Cinema",
                        icon: Film,
                        desc: "Movies & Media",
                        color: "hover:border-purple-500/50 hover:bg-purple-500/5",
                        activeColor:
                          "border-purple-500 bg-purple-500/10 text-purple-500 dark:border-purple-400 dark:text-purple-400",
                      },
                    ].map((scopeOption) => {
                      const Icon = scopeOption.icon
                      const isSelected = newSource.source_scope === scopeOption.id
                      return (
                        <button
                          key={scopeOption.id}
                          type="button"
                          onClick={() =>
                            setNewSource({ ...newSource, source_scope: scopeOption.id as any })
                          }
                          className={`flex flex-col items-center justify-center p-3 rounded-lg border text-center transition-all duration-300 cursor-pointer ${
                            isSelected
                              ? scopeOption.activeColor + " shadow-xs font-semibold"
                              : "border-border bg-card/40 text-muted-foreground " + scopeOption.color
                          }`}
                        >
                          <Icon className="size-5 mb-1 shrink-0" />
                          <span className="text-xs block font-medium">{scopeOption.label}</span>
                          <span className="text-[9px] text-muted-foreground/80 mt-0.5 line-clamp-1">
                            {scopeOption.desc}
                          </span>
                        </button>
                      )
                    })}
                  </div>
                </Field>

                {/* Add to list button */}
                <Button
                  type="submit"
                  className="w-full mt-4 flex items-center justify-center gap-2 py-5 bg-primary text-primary-foreground font-semibold rounded-lg hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 cursor-pointer text-sm"
                >
                  <Plus className="size-4" />
                  Add Source To The List
                </Button>
              </form>
            </div>
          </div>

          {/* Right Column: Ingestion Queue list & Actions */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="rounded-xl border border-border bg-card shadow-xs p-6 flex flex-col min-h-[500px]">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h2 className="font-heading text-xl font-semibold">Staged Ingestion Queue</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Sources waiting deployment to the ingestion nodes
                  </p>
                </div>
                <div className="px-3 py-1 bg-muted text-muted-foreground text-xs font-semibold rounded-full border border-border">
                  {createSources.data.length} {createSources.data.length === 1 ? "source" : "sources"} staged
                </div>
              </div>

              {/* Queue List Area */}
              <div className="flex-1 overflow-y-auto max-h-[360px] pr-2 no-scrollbar">
                {createSources.data.length === 0 ? (
                  /* Empty Queue State */
                  <div className="h-full flex flex-col items-center justify-center border border-dashed border-border rounded-xl p-8 bg-muted/10 min-h-[300px]">
                    <div className="h-16 w-16 rounded-full bg-muted/40 flex items-center justify-center mb-4">
                      <Layers className="size-8 text-muted-foreground/60" />
                    </div>
                    <h3 className="font-heading text-sm font-semibold text-foreground/85">
                      No sources staged
                    </h3>
                    <p className="text-xs text-muted-foreground text-center max-w-sm mt-1">
                      Use the configurator form on the left to add ingestion details. Staged sources will show
                      up here before pushing to production.
                    </p>
                  </div>
                ) : (
                  /* Staged queue list */
                  <div className="flex flex-col gap-3">
                    {createSources.data.map((source, index) => {
                      const scopeBadges = {
                        Technical: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
                        Gaming:
                          "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
                        Cinema:
                          "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20",
                      }
                      return (
                        <div
                          key={index}
                          className="group flex items-center justify-between p-3.5 rounded-lg border border-border bg-card/60 hover:bg-card hover:border-border/80 hover:shadow-xs transition-all duration-300"
                        >
                          <div className="flex items-center gap-3 min-w-0 flex-1">
                            {/* Scope Icon badge */}
                            <div
                              className={`size-10 rounded-lg flex items-center justify-center shrink-0 border ${
                                source.source_scope === "Technical"
                                  ? "bg-blue-500/10 text-blue-500 border-blue-500/15"
                                  : source.source_scope === "Gaming"
                                    ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/15"
                                    : "bg-purple-500/10 text-purple-500 border-purple-500/15"
                              }`}
                            >
                              {source.source_scope === "Technical" && <Code className="size-5 shrink-0" />}
                              {source.source_scope === "Gaming" && <Gamepad2 className="size-5 shrink-0" />}
                              {source.source_scope === "Cinema" && <Film className="size-5 shrink-0" />}
                            </div>

                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-sm truncate">{source.source_name}</span>
                                <span
                                  className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${
                                    scopeBadges[source.source_scope] || ""
                                  }`}
                                >
                                  {source.source_scope}
                                </span>
                              </div>
                              <div className="flex flex-wrap items-center gap-y-0.5 gap-x-3 text-xs text-muted-foreground mt-0.5">
                                <a
                                  href={source.source_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="hover:text-primary hover:underline truncate max-w-[200px]"
                                >
                                  {source.source_url}
                                </a>
                                <span className="text-muted-foreground/35">•</span>
                                <span className="capitalize">{source.source_type}</span>
                                <span className="text-muted-foreground/35">•</span>
                                <span>{source.source_nationality}</span>
                              </div>
                            </div>
                          </div>

                          {/* Action: Delete from list */}
                          <button
                            type="button"
                            onClick={() => handleRemoveSource(index)}
                            className="size-8 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive flex items-center justify-center transition-all duration-300 ml-2 cursor-pointer"
                            title="Remove Source"
                          >
                            <X className="size-4" />
                          </button>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Bottom deployment panel */}
              {createSources.data.length > 0 && (
                <div className="mt-6 pt-6 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="text-xs text-muted-foreground">
                    Staging updates will be pushed in batch processing to live indexing nodes.
                  </div>
                  <Button
                    onClick={uploadTheSources}
                    disabled={createSources.isLoading}
                    className="sm:w-auto w-full flex items-center justify-center gap-2 py-5 px-6 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:-translate-y-0 cursor-pointer text-sm"
                  >
                    {createSources.isLoading ? (
                      <>
                        <Spinner className="text-white" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="size-4" />
                        Upload The Source
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Page
