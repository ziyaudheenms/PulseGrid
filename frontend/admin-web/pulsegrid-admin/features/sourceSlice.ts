import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"
import { Source } from "@/types/source"
import { RootState } from "@/store/store"

interface createSourceArgs {
  token: string
}

export const createSource = createAsyncThunk<
  Source[],
  { token: string },
  { state: RootState }
>("admin/sourceCreate", async ({ token }: createSourceArgs, thunkAPI) => {
  // thunkAPI is used to access the state
  const state = thunkAPI.getState()
  const requestBody: Source[] = state.source.createSources.data // initialState is eliminated because its just a cover  over the state ,the runtime directly mounts all inside the intialstate into root so ->>> state.source.createSource.data    ---------->  .source is the key that is used to configure this slice in the global redux store.

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/v1/datapipeline/admin/source`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      }
    )

    if (!response.ok) {
      const errorData = await response.json()
      return thunkAPI.rejectWithValue(errorData.message || "Request failed")
    }

    return response.json()
  } catch (error: any) {
    return thunkAPI.rejectWithValue(error.message)
  }
})

export const sourceSlice = createSlice({
  name: "source",
  initialState: {
    createSources: {
      status: "idle",
      isLoading: false,
      data: [] as Source[],
      error: null,
    },
    sources: [] as Source[],
  },
  reducers: {
    updateCreateStore: (state, action) => {
      const { sourceDetails } = action.payload
      state.createSources.data = [...state.createSources.data, sourceDetails] //sourceDetails will be added into the exisiting data
      console.log(state.createSources.data, "added data suuccessfully")
    },

    removeTheCreateStoreSource: (state, action) => {
      const { index } = action.payload
      state.createSources.data = state.createSources.data.filter((_, i) => i !== index)
    },
  },

  extraReducers: (builder) => {
    builder
      .addCase(createSource.pending, (state) => {
        state.createSources.isLoading = true
      })
      .addCase(createSource.fulfilled, (state, action) => {
        state.createSources.isLoading = false
        const response = action.payload
        if (response.status_code === 201) {
          console.log(response.data)
        }
      })
      .addCase(createSource.rejected, (state, action) => {
        state.createSources.isLoading = false
      })
  },
})

//used to export the actions -> the inbuild actions present to update the state.
export const { updateCreateStore,removeTheCreateStoreSource } = sourceSlice.actions //actions are the function that which is used here update our state
export default sourceSlice.reducer
