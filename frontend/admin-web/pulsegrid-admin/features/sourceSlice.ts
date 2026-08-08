import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { Source } from "@/types/source";


interface createSourceArgs{
  token: string
}


export const createSource = createAsyncThunk(
  'admin/sourceCreate',
  async ({token}:createSourceArgs, thunkAPI) => {
    // thunkAPI is used to access the state
    const state = thunkAPI.getState();
    const requestBody: Source[] = state.source.createSource.data; // initialState is eliminated because its just a cover  over the state ,the runtime directly mounts all inside the intialstate into root so ->>> state.source.createSource.data    ---------->  .source is the key that is used to configure this slice in the global redux store.

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/v1/datapipeline/admin/source`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      return response.json();
    }
    catch (error:any) {
      return thunkAPI.rejectWithValue(error.message);
    }
  },
)

export const sourceSlice = createSlice({
    name: 'source',
    initialState: {
      createSource: {
        status: 'idle',
        isLoading: false,
        data: [] as Source[],
        error: null
      },
      sources: [] as Source[],
    },
  reducers: {
    updateCreateStore: (state, action) => {
      const { sourceDetails } = action.payload
      state.createSource.data = [...state.createSource.data, sourceDetails]  //sourceDetails will be added into the exisiting data
      }
  },

  extraReducers: (builder) => {
    builder
      .addCase(createSource.pending, (state) => {
        state.createSource.isLoading = true;
      })
      .addCase(createSource.fulfilled, (state, action) => {
        state.createSource.isLoading = false;
        const response = action.payload;
        if (response.status_code === 201) {
          console.log(response.data)
        }
      })
      .addCase(createSource.rejected, (state, action) => {
        state.createSource.isLoading = false;

      });
    },
});

//used to export the actions -> the inbuild actions present to update the state.
export const { updateCreateStore } = sourceSlice.actions;  //actions are the function that which is used here update our state
export default sourceSlice.reducer;
