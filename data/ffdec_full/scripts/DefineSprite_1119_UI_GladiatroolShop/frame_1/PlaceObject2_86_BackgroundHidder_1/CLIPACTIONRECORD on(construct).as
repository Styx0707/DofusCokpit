on(construct){
   while(true)
   {
      if(!(0x08AA2070 & 0x08AA2070))
      {
         if(!ord("\x02"))
         {
            break;
         }
      }
      else
      {
         §§push("enabled");
         §§push(true);
      }
      set(§§pop(),§§pop());
      set("\x18\x05\b",false);
      styleName = "DarkBackgroundHidder";
      break;
   }
}
